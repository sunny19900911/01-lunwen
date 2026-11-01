"""Extract small assembly inputs from five frozen official Example 5 downloads.

No Tcl execution, matrix assembly, modal solution, or response integration.
Raw downloads remain in ignored local-cache. Refuse source drift.
"""
import hashlib
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
CACHE = ROOT / "local-cache"


def save(name, obj):
    (ROOT / name).write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )


def main():
    manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    for item in manifest:
        data = (CACHE / item["file"]).read_bytes()
        assert len(data) == item["bytes"]
        assert hashlib.sha256(data).hexdigest() == item["sha256"]
    source = (CACHE / "Ex5.Frame2D.build.ElasticSection.tcl").read_text()
    required = [
        "set LCol [expr 14*$ft]", "set LBeam [expr 24*$ft]",
        "set Es [expr 29000*$ksi]", "set AgCol [expr 33.5*pow($in,2)]",
        "set IzCol [expr 4090.*pow($in,4)]",
        "set AgBeam [expr 27.7*pow($in,2)]",
        "set IzBeam [expr 2700.*pow($in,4)]",
        "set ColTransfType Linear", "geomTransf Linear $IDBeamTransf",
        "set GammaConcrete [expr 150*$pcf]", "set Tslab [expr 6*$in]",
        "set QBeam [expr 94*$lbf/$ft]", "set QdlCol [expr 114*$lbf/$ft]",
    ]
    assert all(token in source for token in required)
    units = (CACHE / "LibUnits.tcl").read_text()
    assert "set g [expr 32.2*$ft/pow($sec,2)]" in units
    nodes = []
    for tag, x, y in re.findall(r"^node\s+(\d+)\s+\$X(\d+)\s+\$Y(\d+)", source, re.M):
        nodes.append({"tag": int(tag), "x_in": (int(x)-1)*288,
                      "y_in": (int(y)-1)*168})
    fixes = [{"node": int(tag), "fixed_dofs": [int(a), int(b), int(c)]}
             for tag, a, b, c in re.findall(r"^fix\s+(\d+)\s+(\d)\s+(\d)\s+(\d)", source, re.M)]
    elements = []
    for tag, i, j, section in re.findall(
        r"^element nonlinearBeamColumn\s+(\d+)\s+(\d+)\s+(\d+)\s+\$np\s+\$(ColSecTag|BeamSecTag)",
        source, re.M,
    ):
        elements.append({"tag": int(tag), "i": int(i), "j": int(j),
                         "section": "column" if section == "ColSecTag" else "beam"})
    masses_in_source = re.findall(r"^mass\s+(\d+)\s+\[expr\s+(.+?)\]\s+0\.\s+0\.", source, re.M)
    assert len(nodes) == 16 and len(fixes) == 4 and len(elements) == 21
    assert len(masses_in_source) == 12
    assert all(x["fixed_dofs"] == [1, 1, 0] for x in fixes)
    assert not re.search(r"^\s*(equalDOF|rigidDiaphragm)\b", source, re.M)
    # Unit conversion/arithmetic only, retaining exact original nodal allocation.
    g = 32.2 * 12
    column_weight = (114 * 0.001 / 12) * 168
    beam_weight = ((150 * 0.001 / 12**3) * 6 * 288 + 94 * 0.001 / 12) * 288
    masses = []
    for tag_text, expression in masses_in_source:
        assert expression.endswith("/$g")
        assert not expression.replace("$WeightCol/2", "").replace("$WeightBeam/2", "").replace("/$g", "").strip(" (+)")
        weight = expression.count("$WeightCol/2") * column_weight / 2
        weight += expression.count("$WeightBeam/2") * beam_weight / 2
        masses.append({"node": int(tag_text), "mx_kip_s2_per_in": weight/g,
                       "my": 0, "mtheta": 0, "source_expression": expression})
    model = {
        "identity": "OpenSees official Example 5, 3-story 3-bay, ElasticSection branch",
        "authors_in_source": "Silvia Mazzoni & Frank McKenna, 2006",
        "status": "public numerical example, not a measured real building",
        "units": {"length": "in", "force": "kip", "time": "s", "mass": "kip*s^2/in"},
        "dof_per_node": ["ux", "uy", "rz"], "stories": 3, "bays": 3,
        "E_kip_per_in2": 29000,
        "sections": {"column": {"A_in2": 33.5, "Iz_in4": 4090},
                     "beam": {"A_in2": 27.7, "Iz_in4": 2700}},
        "geometry": "Linear", "section_response": "Elastic",
        "original_element": "nonlinearBeamColumn, five integration points, elastic section",
        "nodes": nodes, "supports": fixes, "elements": elements, "nodal_masses": masses,
        "g_in_per_s2": g,
        "derived_weights_kip": {"each_column": column_weight, "each_beam_and_slab": beam_weight},
        "floor_mass_kip_s2_per_in": {
            str(level): sum(x["mx_kip_s2_per_in"] for x in masses if x["node"]//10 == level)
            for level in (2, 3, 4)
        },
        "assembly_handoff": {
            "full_dofs": 48, "free_dofs_after_supports": 40,
            "positive_mass_horizontal_dofs": 12, "massless_free_dofs": 28,
            "no_diaphragm_constraint": True,
            "suggestion": "Assemble linear 2D frame K; statically condense 28 massless DOFs only after checking Kzz invertibility. Preserve all 12 horizontal DOFs.",
            "not_performed_here": ["matrix assembly", "modal analysis", "response prediction", "solver invocation"],
        },
    }
    record_path = CACHE / "H-E12140.AT2"
    raw = record_path.read_bytes()
    lines = raw.decode("ascii").splitlines()
    # The file has doubled CR line breaks. Keep nonempty header lines explicitly.
    lines = [line for line in lines if line.strip()]
    header = lines[:4]
    npts = int(re.search(r"NPTS=\s*(\d+)", header[3]).group(1))
    dt = float(re.search(r"DT=\s*([.\d]+)", header[3]).group(1))
    values = [float(x) for x in " ".join(lines[4:]).split()]
    assert len(values) == npts == 7802 and dt == 0.005
    assert all(math.isfinite(x) for x in values)
    record = {
        "file": record_path.name, "raw_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(), "header": header,
        "event": "Imperial Valley", "date_and_time_as_header": "10/15/79 2316",
        "station": "El Centro Array #12, USGS station 931", "component_degrees": 140,
        "header_timezone": "not stated", "units": "g", "npts": npts, "dt_s": dt,
        "span_if_first_sample_t0_s": (npts-1)*dt,
        "first_sample_t0": "index-zero convention must be frozen by experiment owner",
        "filter_header": "HP=0.1 Hz LP=40.0 Hz",
        "numeric_integrity": {"count_matches_header": True, "all_finite": True,
                              "min_g": min(values), "max_g": max(values), "pga_abs_g": max(map(abs, values))},
        "original_analysis": {"GMfact": 1.5, "g_in_per_s2": g,
                              "dt_analysis_s": 0.01, "Tmax_analysis_s": 10.0,
                              "damping": "Rayleigh, target 0.02 at modes 1 and 3"},
        "license_status": "public download; separate record redistribution license not established; raw file local cache only",
    }
    save("assembly-inputs.json", model)
    save("record-metadata.json", record)
    print(json.dumps({"nodes": len(nodes), "elements": len(elements), "masses": len(masses),
                      "floor_masses": model["floor_mass_kip_s2_per_in"],
                      "record": record}, ensure_ascii=False))


if __name__ == "__main__":
    main()
