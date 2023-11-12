import { SModel } from "../src/model/smodel";
import { parseModelHeader } from "../src/model/builder/model_builder";
import { loadSolutions, parseXml } from "../src/file_parser";

import { assert } from "chai";
import { SRepository } from "../src/model/srepository";
import { SNode, SNodeRef } from "../src/model/snode";

describe("testing building of the model from a directory with solutions", () => {
  it("solutions dir", () => {
    const repo: SRepository = loadSolutions(
      "..\\mps_test_projects\\mps_cli_lanuse_file_per_root",
    );
    assert.equal(repo.modules.length, 2);

    assert.equal(repo.getNodesWithPropertyAndValue("name").length, 15)
    assert.equal(repo.getNodesWithPropertyAndValue("name", "Mark Twain").length, 1)
    const markTwain = repo.getNodesWithPropertyAndValue("name", "Mark Twain")[0]

    assert.equal(repo.getNodesWithPropertyAndValue("name", "Tom Sawyer").length, 2)
    const tomSawyer = repo.getNodesWithPropertyAndValue("name", "Tom Sawyer")[0]
    assert.equal(tomSawyer.getLinkedNodes("authors").length, 1)
    const markTwainRef = tomSawyer.getLinkedNodes("authors")[0]

    assert.equal((markTwainRef as SNode).getLinkedNodes("person").length, 1)
    
    assert.equal(markTwain, (((markTwainRef as SNode).getLinkedNodes("person")[0]) as SNodeRef).resolve(repo))
  });
});
