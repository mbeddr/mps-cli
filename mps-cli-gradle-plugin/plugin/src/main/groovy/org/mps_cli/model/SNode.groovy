package org.mps_cli.model

class SNode {
    SModel myModel
    SNode parentNode
    def roleInParent
    def concept = ""
    def id
    def properties = [:]
    def List<SNode> children = []
    def Map<String,SNodeRef> refs = [:]

    SNode(parent, role, model) {
        parentNode = parent
        roleInParent = role
        myModel = model
        if (parent != null)
            parent.children.add(this)
    }

    def descendants(includeSelf = false) {
        def nodesToVisit = children
        def res = []
        while (!nodesToVisit.isEmpty()) {
            def crtNode = nodesToVisit.first()
            nodesToVisit.remove(crtNode)
            res.add(crtNode)
            nodesToVisit.addAll(crtNode.children)
        }
        if (includeSelf) res.add(this)
        res
    }
}
