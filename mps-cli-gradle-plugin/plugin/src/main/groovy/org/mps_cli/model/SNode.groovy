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

    def propertyMissing( name ) {
        def val = properties[name]
        if (val != null) return val
        val = children.findAll( {it.roleInParent.equals(name) })
        if (val != null && !val.isEmpty()) return val
        refs[name]
    }
}
