package org.mps_cli.model.builder

import org.mps_cli.model.SConcept
import org.mps_cli.model.SLanguage

class SLanguageBuilder {

    private static Map<String, SLanguage> languageMap = new HashMap<>()
    private static Map<String, SConcept> conceptMap = new HashMap<>()

    static List<SLanguage> allLanguages() {
        languageMap.values().toList()
    }

    static SLanguage getLanguage(String lanName) {
        SLanguage lan = languageMap.get(lanName)
        if (lan == null) {
            lan = new SLanguage(name: lanName)
            languageMap.put(lanName, lan)
        }
        lan
    }

    static SConcept getConcept(SLanguage lan, String conceptName) {
        SConcept concept = conceptMap.get(conceptName)
        if (concept == null) {
            concept = new SConcept(name: conceptName)
            lan.concepts.add(concept)
            conceptMap.put(conceptName, concept)
        }
        concept
    }

    static def clear() {
        languageMap.clear()
        conceptMap.clear()
    }

}
