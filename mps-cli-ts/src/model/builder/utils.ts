

export function childrenByTagName(element : Element, tagName : string) : Element[] {
    const res : Element[] = []

    for(const child of element.children) {
        if (child.tagName == tagName) {
            res.push(child);
        }
    }

    return res
}

export function firstChildByTagName(element : Element, tagName : string) : Element | null {
    for(const child of element.children) {
        if (child.tagName == tagName) {
            return child
        }
    }
    return null
}