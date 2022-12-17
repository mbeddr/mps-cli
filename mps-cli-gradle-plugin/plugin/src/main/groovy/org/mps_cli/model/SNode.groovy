package org.mps_cli.model

class SNode {
    SModel myModel
    SNode parentNode
    String roleInParent
    SConcept concept
    String id
    def properties = [:]
    List<SNode> children = []
    Map<String,SNodeRef> refs = [:]

    SNode(SNode parent, String role, SModel model) {
        parentNode = parent
        roleInParent = role
        myModel = model
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
        if (val != null && !val.isEmpty()) {
            if (val.size() > 1) return val
            return val.first()
        }
        refs[name]
    }
}
