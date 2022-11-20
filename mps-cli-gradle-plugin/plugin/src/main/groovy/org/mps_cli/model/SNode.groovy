package org.mps_cli.model

class SNode {
    def SNode parentNode
    def roleInParent
    def concept = ""
    def id
    def properties = [:]
    def List<SNode> children = []

    SNode(parent, role) {
        parentNode = parent
        roleInParent = role
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
