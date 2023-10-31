import { SLanguage } from "./slanguage"

export class SModel {
    name : string
    id : string
    usedLanguages : SLanguage[]

    constructor(name : string, id : string) {
        this.name = name
        this.id = id
        this.usedLanguages = []
    }

}