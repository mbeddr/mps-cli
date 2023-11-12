
import { SModel } from '../smodel';
import { SSolution } from '../smodule';
import { SLanguageBuilder } from './slanguage_builder';

export function buildSolution(doc : Document) : SSolution {
    const solutionNode : Element = doc.getElementsByTagName("solution")[0];
    const name = solutionNode.attributes.getNamedItem("name")?.value!
    const id = solutionNode.attributes.getNamedItem("uuid")?.value!
 
    const mySSolution = new SSolution(name, id);
    return mySSolution;
}