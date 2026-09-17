"""Behavioral checks in isolated temporary projects; no production approvals."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import rfp_intake as rfp


TEXT = "The contractor shall protect all existing utilities and submit a site safety plan before starting demolition work."


def make_pdf(path, text=TEXT):
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
    writer = PdfWriter()
    p = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject({NameObject("/Type"):NameObject("/Font"),NameObject("/Subtype"):NameObject("/Type1"),NameObject("/BaseFont"):NameObject("/Helvetica")})
    p[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"):DictionaryObject({NameObject("/F1"):writer._add_object(font)})})
    content = DecodedStreamObject()
    # Short lines keep all characters inside the physical page.
    words = text.split()
    lines = [" ".join(words[i:i+10]) for i in range(0,len(words),10)]
    instructions = ["BT /F1 11 Tf 48 730 Td 16 TL"]
    for line in lines:
        escaped=line.replace("\\", "\\\\").replace("(","\\(").replace(")","\\)")
        instructions.append(f"({escaped}) Tj T*")
    instructions.append("ET")
    content.set_data("\n".join(instructions).encode("ascii"))
    p[NameObject("/Contents")] = writer._add_object(content)
    with path.open("wb") as f:
        writer.write(f)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="rfp-intake-test-")
        self.root=Path(self.tmp.name)
        self.source=self.root/"input"
        self.source.mkdir()
        self.project=self.root/"packet"
        make_pdf(self.source/"Solicitation.pdf")
        self.run_ingest()

    def tearDown(self):
        self.tmp.cleanup()

    def run_ingest(self):
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            rfp.ingest(argparse.Namespace(project=str(self.project),source=str(self.source),name="Fixture",exclude=[]))

    def batch(self, bid="TEST-001"):
        s=rfp.load(self.project)
        return {"batch_id":bid,"snapshot":s["snapshot"]}

    def record(self, rid="REQ-001", quote=TEXT):
        s=rfp.load(self.project)
        eid=next(iter(s["evidence"]))
        return {"record_id":rid,"type":"requirement","title":"Protect utilities","interpretation":"Protect utilities and submit safety plan before work.",
                "contract_layer":"project","applicability":"Before demolition","tags":["utilities","safety"],"critical":True,"always_include":True,
                "authority_status":"unverified","review_status":"ai_draft","evidence_ids":[eid],"citations":[{"evidence_id":eid,"quote":quote}],"details":{}}

    def apply(self,batch):
        path=self.root/(batch["batch_id"]+".json")
        rfp.dump(path,batch)
        with contextlib.redirect_stdout(io.StringIO()):
            rfp.import_batch(argparse.Namespace(project=str(self.project),batch=str(path)))

    def release(self):
        s=rfp.load(self.project)
        b=self.batch("TEST-RELEASE")
        b["records"]=[self.record()]
        b["expected_documents"]=[{"expected_id":"EXPECTED-001","title":"Fixture solicitation","evidence_ids":[next(iter(s["evidence"]))],
                                  "matched_document_ids":[next(iter(s["documents"]))],"version_verified":True,"note":"Synthetic fixture only"}]
        b["section_reviews"]=[{"section_id":sid,"covered_evidence_ids":sec["evidence_ids"],"status":"ai_reviewed",
                               "reviewer":"Test fixture agent","coverage_note":"Entire synthetic fixture reviewed"} for sid,sec in s["sections"].items()]
        b["attestations"]=[{"kind":k,"human_approved":True,"reviewer":"Synthetic test reviewer only","note":"Test fixture, not a real approval"} for k in sorted(rfp.ATTESTATIONS)]
        self.apply(b)
        self.assertTrue(rfp.compute_gate(self.project,rfp.load(self.project))["estimating_allowed"])

    def test_duplicate_and_noop_are_cached_and_sources_preserved(self):
        original_hash=rfp.sha(self.source/"Solicitation.pdf")
        shutil.copy2(self.source/"Solicitation.pdf",self.source/"Copy.pdf")
        self.run_ingest()
        s=rfp.load(self.project)
        self.assertEqual(len(s["files"]),2)
        self.assertEqual(len(s["documents"]),1)
        self.assertEqual(len(s["evidence"]),1)
        self.run_ingest()
        s2=rfp.load(self.project)
        self.assertEqual(s["snapshot"],s2["snapshot"])
        self.assertEqual(s["change_reports"],s2["change_reports"])
        self.assertEqual(original_hash,rfp.sha(self.source/"Solicitation.pdf"))

    def test_fabricated_quote_rejected_atomically(self):
        b=self.batch()
        b["records"]=[self.record(quote="The government waives all requirements.")]
        before=rfp.sha(self.project/rfp.INTAKE/"state.json")
        with self.assertRaisesRegex(ValueError,"Quote does not match"):
            self.apply(b)
        self.assertEqual(before,rfp.sha(self.project/rfp.INTAKE/"state.json"))
        self.assertFalse((self.project/rfp.INTAKE/"review_batches"/"TEST-001.json").exists())

    def test_dangling_relationship_rejected(self):
        b=self.batch()
        b["records"]=[self.record()]
        b["relationships"]=[{"relationship_id":"REL-1","from_id":"REQ-001","to_id":"SC-MISSING","relation":"requires","evidence_ids":self.record()["evidence_ids"]}]
        with self.assertRaisesRegex(ValueError,"endpoints"):
            self.apply(b)
        self.assertEqual(rfp.load(self.project)["records"],{})

    def test_supersession_requires_human_and_cannot_cycle(self):
        b=self.batch()
        b["records"]=[self.record(),self.record("REQ-002")]
        edge={"relationship_id":"REL-1","from_id":"REQ-002","to_id":"REQ-001","relation":"supersedes","evidence_ids":self.record()["evidence_ids"]}
        b["relationships"]=[edge]
        with self.assertRaisesRegex(ValueError,"explicit human approval"):
            self.apply(b)
        edge.update(human_approved=True,reviewer="Synthetic test reviewer",decision_note="Fixture only")
        b["relationships"].append(dict(edge,relationship_id="REL-2",from_id="REQ-001",to_id="REQ-002"))
        with self.assertRaisesRegex(ValueError,"cycle"):
            self.apply(b)

    def test_valid_ready_path_and_estimate_links_preserve_release(self):
        self.release()
        b=self.batch("TEST-LINK")
        b["estimate_links"]=[{"estimate_line_id":"EST-1","record_id":"REQ-001","estimate_file":"04_ESTIMATING/test.json"}]
        self.apply(b)
        self.assertTrue(rfp.compute_gate(self.project,rfp.load(self.project))["estimating_allowed"])

    def test_live_added_document_blocks_before_ingest(self):
        self.release()
        make_pdf(self.source/"Amendment02.pdf",TEXT+" Amendment changes the utility requirements.")
        gate=rfp.compute_gate(self.project,rfp.load(self.project))
        self.assertFalse(gate["estimating_allowed"])
        self.assertIn("source_folder_changed",gate["blockers_by_kind"])

    def test_amendment_invalidates_release_and_marks_estimate_impacts(self):
        self.release()
        b=self.batch("TEST-LINK")
        b["estimate_links"]=[{"estimate_line_id":"EST-1","record_id":"REQ-001","estimate_file":"04_ESTIMATING/test.json"}]
        self.apply(b)
        old=rfp.load(self.project)
        make_pdf(self.source/"Amendment02.pdf",TEXT+" Amendment changes the utility requirements.")
        self.run_ingest()
        s=rfp.load(self.project)
        self.assertNotEqual(old["snapshot"],s["snapshot"])
        self.assertIn("REQ-001",s["records"])
        self.assertFalse(rfp.compute_gate(self.project,s)["estimating_allowed"])
        self.assertEqual(s["change_reports"][-1]["estimate_lines_requiring_review"][0]["estimate_line_id"],"EST-1")
        self.assertIn("REQ-001",s["change_reports"][-1]["affected_records"])

    def test_source_and_extraction_tampering_block(self):
        self.release()
        s=rfp.load(self.project)
        d=next(iter(s["documents"].values()))
        (self.project/d["source_path"]).write_bytes(b"changed")
        self.assertIn("source_integrity",rfp.compute_gate(self.project,s)["blockers_by_kind"])
        shutil.copy2(self.source/"Solicitation.pdf",self.project/d["source_path"])
        artifact=next(iter(d["extraction_hashes"]))
        (self.project/artifact).write_text("changed")
        self.assertIn("extraction_integrity",rfp.compute_gate(self.project,s)["blockers_by_kind"])

    def test_new_semantic_record_invalidates_release(self):
        self.release()
        b=self.batch("TEST-NEW-RECORD")
        b["records"]=[self.record("REQ-002")]
        self.apply(b)
        gate=rfp.compute_gate(self.project,rfp.load(self.project))
        self.assertFalse(gate["estimating_allowed"])
        self.assertEqual(gate["blockers_by_kind"]["human_review"],4)

    def test_unread_section_cannot_be_marked_covered(self):
        s=rfp.load(self.project)
        b=self.batch()
        b["section_reviews"]=[{"section_id":next(iter(s["sections"])),"covered_evidence_ids":["EV-FAKE"],
                               "status":"ai_reviewed","reviewer":"Agent","coverage_note":"Fixture only"}]
        with self.assertRaisesRegex(ValueError,"every evidence unit"):
            self.apply(b)

    def test_unsupported_source_blocks(self):
        (self.source/"plan.dwg").write_bytes(b"unsupported fixture")
        self.run_ingest()
        gate=rfp.compute_gate(self.project,rfp.load(self.project))
        self.assertIn("extraction_failure",gate["blockers_by_kind"])
        self.assertFalse(gate["estimating_allowed"])

    def test_packet_estimating_blocks_and_research_is_explicit(self):
        args=argparse.Namespace(project=str(self.project),query="utilities",mode="estimating",limit=2,output=None)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(rfp.packet(args),2)
        args.mode="research"
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(rfp.packet(args),0)
        result=json.loads(out.getvalue())
        self.assertFalse(result["estimating_allowed"])
        self.assertFalse(result["completeness_claim"])
        self.assertTrue(result["evidence"])

    def test_conflict_context_is_not_dropped(self):
        b=self.batch()
        b["records"]=[self.record(),self.record("REQ-002")]
        b["records"][1].update(title="Alternate interpretation",tags=["other"],always_include=False)
        b["relationships"]=[{"relationship_id":"REL-1","from_id":"REQ-001","to_id":"REQ-002","relation":"conflicts_with","evidence_ids":self.record()["evidence_ids"]}]
        self.apply(b)
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            rfp.packet(argparse.Namespace(project=str(self.project),query="utilities",mode="research",limit=1,output=None))
        result=json.loads(out.getvalue())
        self.assertEqual({r["record_id"] for r in result["records"]},{"REQ-001","REQ-002"})
        self.assertTrue(any(b["kind"]=="authority_conflict" for b in result["blockers"]))

    def get_packet(self, **kwargs):
        args = dict(project=str(self.project), query="utilities", mode="research", limit=2,
                    output=None, view="summary", max_chars=6000, cursor=None, record_id=[], evidence_id=[])
        args.update(kwargs)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(rfp.packet(argparse.Namespace(**args)), 0)
        payload = out.getvalue()
        value = json.loads(payload)
        self.assertLessEqual(len(payload), args["max_chars"])
        self.assertEqual(value["usage"]["serialized_characters"], len(payload))
        self.assertEqual(value["usage"]["utf8_bytes"], len(payload.encode("utf-8")))
        return value

    def collect_pages(self, **kwargs):
        result = {k: [] for k in ("records", "relationships", "evidence", "blockers")}
        fragments = {}
        cursor = None
        pages = []
        for _ in range(300):
            page = self.get_packet(cursor=cursor, **kwargs)
            pages.append(page)
            for key in result:
                result[key].extend(page[key])
            for fragment in page["fragments"]:
                fragments.setdefault(fragment["item_id"], []).append(fragment)
            cursor = page["pagination"]["next_cursor"]
            if not cursor:
                break
        else:
            self.fail("Paging failed to terminate")
        for parts in fragments.values():
            parts.sort(key=lambda p: p["part"])
            self.assertEqual([p["part"] for p in parts], list(range(1, parts[0]["parts"] + 1)))
            result[parts[0]["collection"]].append(json.loads("".join(p["json_fragment"] for p in parts)))
        return result, pages

    def test_summary_omits_raw_text_but_full_retrieves_exact_evidence(self):
        b = self.batch()
        b["records"] = [self.record()]
        self.apply(b)
        summary, _ = self.collect_pages()
        self.assertNotIn("text", summary["evidence"][0])
        self.assertNotIn("citations", summary["records"][0])
        self.assertIn("source_sha256", summary["evidence"][0])
        full, _ = self.collect_pages(view="full", record_id=["REQ-001"], query="")
        self.assertEqual(full["records"][0], self.record())
        self.assertEqual(full["evidence"][0]["text"], next(iter(rfp.load(self.project)["evidence"].values()))["text"])

    def test_paging_preserves_common_conflicting_records_and_all_links(self):
        b = self.batch()
        b["records"] = [self.record(f"REQ-{i:03}") for i in range(40)]
        b["relationships"] = [{"relationship_id": "REL-TEST", "from_id": "REQ-000", "to_id": "REQ-039",
                               "relation": "conflicts_with", "evidence_ids": self.record()["evidence_ids"]}]
        self.apply(b)
        before = rfp.sha(self.project/rfp.INTAKE/"state.json")
        result, pages = self.collect_pages(max_chars=5000)
        self.assertGreater(len(pages), 1)
        self.assertEqual(len(result["records"]), 40)
        self.assertEqual({r["record_id"] for r in result["records"]}, {r["record_id"] for r in b["records"]})
        self.assertEqual(result["relationships"], b["relationships"])
        self.assertEqual(pages[0]["totals"]["common_records"], 40)
        self.assertEqual(pages[0]["totals"]["conflict_relationships"], 1)
        self.assertEqual(before, rfp.sha(self.project/rfp.INTAKE/"state.json"))

    def test_oversized_unicode_record_reassembles_without_loss(self):
        b = self.batch()
        record = self.record()
        record["interpretation"] = 'Preserve “条件” and \\ punctuation. ' * 700
        b["records"] = [record]
        self.apply(b)
        result, pages = self.collect_pages(view="full", max_chars=4000)
        self.assertEqual(result["records"], [record])
        self.assertTrue(any(p["fragments"] for p in pages))

    def test_cursor_rejects_changed_query_budget_and_review_data(self):
        b = self.batch()
        b["records"] = [self.record(f"REQ-{i:03}") for i in range(12)]
        self.apply(b)
        cursor = self.get_packet(max_chars=4000)["pagination"]["next_cursor"]
        self.assertIsNotNone(cursor)
        with self.assertRaisesRegex(ValueError, "Stale cursor"):
            self.get_packet(cursor=cursor, max_chars=4000, query="safety")
        with self.assertRaisesRegex(ValueError, "Stale cursor"):
            self.get_packet(cursor=cursor, max_chars=5000)
        b = self.batch("TEST-CHANGE")
        b["records"] = [self.record("REQ-999")]
        self.apply(b)
        with self.assertRaisesRegex(ValueError, "Stale cursor"):
            self.get_packet(cursor=cursor, max_chars=4000)

    def test_blocker_view_preserves_every_blocker(self):
        expected = rfp.compute_gate(self.project, rfp.load(self.project))["blockers"]
        result, pages = self.collect_pages(view="blockers", query="", max_chars=4000)
        self.assertCountEqual(result["blockers"], expected)
        self.assertEqual(pages[0]["totals"]["blockers"], len(expected))

    def test_packet_rejects_unknown_ids_and_invalid_budget(self):
        with self.assertRaisesRegex(ValueError, "Unknown record"):
            self.get_packet(record_id=["REQ-NOT-THERE"])
        with self.assertRaisesRegex(ValueError, "max-chars"):
            self.get_packet(max_chars=10)

    def test_context_cache_tampering_is_detected(self):
        result = self.get_packet()
        archive = self.project/result["full_context_file"]
        archive.write_text('{}')
        with self.assertRaisesRegex(ValueError, "Cached context was modified"):
            self.get_packet()


    def test_stored_paths_are_portable_across_operating_systems(self):
        sub=self.source/"Attachments"/"Nested"
        sub.mkdir(parents=True)
        make_pdf(sub/"Drawing Index.pdf","Sheet index listing civil drawings C-101 through C-104 for the project site.")
        self.run_ingest()
        s=rfp.load(self.project)
        paths=[f["relative_path"] for f in s["files"]]+[d["source_path"] for d in s["documents"].values()]
        paths+=[e["text_path"] for e in s["evidence"].values() if e.get("text_path")]+[x["path"] for x in s["sections"].values()]
        paths+=[k for d in s["documents"].values() for k in d.get("extraction_hashes",{})]
        self.assertIn("Attachments/Nested/Drawing Index.pdf",paths)
        self.assertFalse([p for p in paths if "\\" in p])
        for p in paths[len(s["files"]):]:
            self.assertTrue((self.project/p).is_file(),p)
        self.assertNotIn("\r\r\n",(self.project/rfp.INTAKE/"review_queue.csv").read_bytes().decode("utf-8"))
        self.assertTrue(rfp.compute_gate(self.project,s)["pdf_pages"]>=2)

    def test_project_lock_rejects_concurrent_commands(self):
        with rfp.project_lock(self.project):
            if rfp.os.name=="nt":
                with self.assertRaisesRegex(OSError,"in use"):
                    with rfp.project_lock(self.project):
                        pass
        with rfp.project_lock(self.project):
            pass

    def test_unicode_output_survives_legacy_console_encoding(self):
        raw=io.BytesIO()
        stream=io.TextIOWrapper(raw,encoding="cp1252")
        with contextlib.redirect_stdout(stream):
            rfp.utf8_console()
            print("Amendment 02 — ≤ 30 days “quoted”")
        stream.flush()
        self.assertIn("—".encode("utf-8"),raw.getvalue())


if __name__=="__main__":
    unittest.main(verbosity=2)
