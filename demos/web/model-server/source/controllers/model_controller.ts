import { Request, Response, NextFunction } from 'express';
import axios, { AxiosResponse } from 'axios';

import { loadSolutions } from '../../../../../mps-cli-ts/src/file_parser'
import { SRepository } from '../../../../../mps-cli-ts/src/model/srepository';
import { SSolution } from '../../../../../mps-cli-ts/src/model/smodule';
import { SModel } from '../../../../../mps-cli-ts/src/model/smodel';

var repo : SRepository;

// getting all solutions
const getSolutions = async (req: Request, res: Response, next: NextFunction) => {
    repo = loadSolutions('../../../mps_test_projects/mps_cli_lanuse_file_per_root')

    let emptySolutions = repo.modules.map( it => new SSolution(it.name, it.id) )
    return res.status(200).json({
        message: emptySolutions
    });
};

// getting models of a solution
const getModelsOfSolution = async (req: Request, res: Response, next: NextFunction) => {
    // get the solution id from the req
    let solutionId: string = req.params.solutionId;
    
    let sol = repo.findModuleById(solutionId)
    let emptyModels = sol?.models.map( it => new SModel(it.name, it.id ))
    return res.status(200).json({
        message: emptyModels
    });
};

// getting root nodes of a model
const getRootsOfModel = async (req: Request, res: Response, next: NextFunction) => {
    // get the model id from the req
    let modelId: string = req.params.id;
    
    let model = repo.findModelById(modelId)
    return res.status(200).json({
        message: model?.rootNodes
    });
};

export default { getSolutions, getModelsOfSolution };