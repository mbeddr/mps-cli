

export function childrenByTagName(element : Element, tagName : string) : Element[] {
    const res : Element[] = []

    console.log("children " + element.children.length)
    console.log("node list " + element.childNodes.length)
    console.log(element)

    for(const child of element.children) {

        console.log(element.tagName + " children: " + child.tagName)

        if (child.tagName == tagName) {
            res.push(child);
        }
    }

    return res
}