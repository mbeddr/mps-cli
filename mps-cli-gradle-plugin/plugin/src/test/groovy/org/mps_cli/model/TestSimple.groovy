package org.mps_cli.model

import org.mps_cli.model.builder.BuildingDepthEnum
import spock.lang.Specification
import org.mps_cli.model.builder.SModulesRepositoryBuilder

class TestSimple extends Specification {

    def "'buildModel' task starts"() {
        given:
            def builder = new SModulesRepositoryBuilder(buildingStrategy: BuildingDepthEnum.COMPLETE_MODEL)
        when:
            def repo = builder.build('../../mps_test_projects/mps_cli_landefs/languages')
        then:
            repo.modules.size() == 2
            def languagesNamespaces = repo.modules.collect {it.namespace }
            languagesNamespaces.contains("mps.cli.landefs.library")
            languagesNamespaces.contains("mps.cli.landefs.people")

            def definedConceptsNames = repo.nodesOfShortConceptName("ConceptDeclaration").collect {it.name }
            definedConceptsNames.contains("Library")
            definedConceptsNames.contains("LibraryEntityBase")
            definedConceptsNames.contains("Person")
    }

}
