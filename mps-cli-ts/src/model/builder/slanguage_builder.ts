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
        for(var concept of language.concepts) {
            if (concept.name == name)
                return concept;
        }
        var res = new SConcept(name, id);
        language.concepts.push(res)
        return res;
    }

    static getProperty(concept : SConcept, name : string, id : string) : SProperty {
        return this.getOrCreateSpecificLink(concept, name, id, "property");
    }

    static getChildLink(concept : SConcept, name : string, id : string) : SChildLink {
        return this.getOrCreateSpecificLink(concept, name, id, "child");
    }

    static getReferenceLink(concept : SConcept, name : string, id : string) : SChildLink {
        return this.getOrCreateSpecificLink(concept, name, id, "reference");
    }

    static getOrCreateSpecificLink(concept : SConcept, name : string, id : string, linkType : string) : SAbstractConceptLink {
        for(var link of concept.links) {
            if (link.id == id)
                return link;
        }
        var res;
        if(linkType == "property")
            res = new SProperty(name, id);
        else if(linkType == "child")
            res = new SChildLink(name, id)
        else 
            res = new SReferenceLink(name, id)
        concept.links.push(res)
        return res;
    }
}