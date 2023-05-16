package org.mps_cli.model

class SLanguageModule extends SModuleBase {
    String namespace

    @Override
    String name() {
        return namespace
    }
}
