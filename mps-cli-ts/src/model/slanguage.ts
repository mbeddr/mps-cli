import { SConcept } from "./sconcept";

export class SLanguage {
    name : string;
    id : string;

    concepts = new Map<string, SConcept>

    constructor(name : string, id : string) {
        this.name = name;
        this.id = id;
    }
}