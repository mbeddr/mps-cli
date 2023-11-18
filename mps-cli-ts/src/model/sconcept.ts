

export class SConcept {
    name : string;
    id : string;
    links = new Map<string, SAbstractConceptLink>()
    properties = new Map<string, SProperty>() 

    constructor(name : string, id : string) {
        this.name = name;
        this.id = id;
    }

}

export abstract class SAbstractConceptLink {
    name : string;
    id : string;
    
    constructor(name : string, id : string) {
        this.name = name
        this.id = id
    }
}

export class SProperty {
    name : string;
    id : string;
    
    constructor(name : string, id : string) {
        this.name = name
        this.id = id
    }
} 

export class SChildLink extends SAbstractConceptLink {
    constructor(name : string, id : string) {
        super(name, id)
    }
}

export class SReferenceLink extends SAbstractConceptLink {
    constructor(name : string, id : string) {
        super(name, id)
    }
}