import { SConcept } from "./sconcept";

export class SLanguage {
    name : string;
    id : string;

    concepts : SConcept[] = []

    constructor(name : string, id : string) {
        this.name = name;
        this.id = id;
    }
}