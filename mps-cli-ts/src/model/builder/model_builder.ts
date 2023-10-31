
import { SModel } from '../smodel';
import { SLanguageBuilder } from './slanguage_builder';

export function parseModelHeader(doc : Document) : SModel {
    const modelNode : Element = doc.getElementsByTagName("model")[0];
    const ref = modelNode?.attributes.getNamedItem("ref")?.value
    const id = ref?.substring(0, ref.indexOf("("))!
    const name = ref?.substring(ref.indexOf("(") + 1, ref.length - 1)!

    const mySModel = new SModel(name, id);
    const usedLanguagesNode = modelNode.getElementsByTagName("languages")[0];
    for (var use of usedLanguagesNode.getElementsByTagName("use")) {
        const lan = SLanguageBuilder.getLanguage(use.getAttribute("name")!, use.getAttribute("id")!);
        mySModel.usedLanguages.push(lan)
    }
    return mySModel;
}