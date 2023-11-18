import { SAbstractConceptLink, SChildLink, SConcept, SProperty, SReferenceLink } from "../sconcept";
import { SLanguage } from "../slanguage";


export class SLanguageBuilder {

    static ids2languagesMap : Map<string, SLanguage> = new Map<string, SLanguage>;

    static getLanguage(name : string, id : string) : SLanguage {
        var lan = this.ids2languagesMap.get(id)
        if (lan == undefined) {
            lan = new SLanguage(name, id);
            this.ids2languagesMap.set(id, lan);
6        }
        return lan!;
    }

    static getConcept(language : SLanguage, name : string, id : string) : SConcept {
        var res = language.concepts.get(id)
        if (res === undefined) {
            res = new SConcept(name, id);
            language.concepts.set(id, res)
        }
        return res;
    }

    static getProperty(concept : SConcept, name : string, id : string) : SProperty {
        var res = concept.properties.get(id)
        if (res === undefined) {
            res = new SProperty(name, id)
            concept.properties.set(id, res)
        } 
        return res;
    }

    static getChildLink(concept : SConcept, name : string, id : string) : SChildLink {
        var res = concept.links.get(id)
        if (res === undefined) {
            res = new SChildLink(name, id)
            concept.links.set(id, res)
        } 
        return res;
    }

    static getReferenceLink(concept : SConcept, name : string, id : string) : SReferenceLink {
        var res = concept.links.get(id)
        if (res === undefined) {
            res = new SReferenceLink(name, id)
            concept.links.set(id, res)
        } 
        return res;
    }
}