#  Copyright (c) ZenML GmbH 2020. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
from abc import abstractmethod
from typing import Any

from zenml.artifacts import DataArtifact
from zenml.steps.base_step import BaseStep
from zenml.steps.base_step_config import BaseStepConfig
from zenml.steps.step_output import Output


class BaseSplitStepConfig(BaseStepConfig):
    """Base class for split configs to inherit from"""


class BaseSplitStep(BaseStep):
    """Base step implementation for any split step implementation on ZenML
    """
    STEP_INNER_FUNC_NAME = "split_fn"

    def process(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def split_fn(
            self,
            dataset: DataArtifact,
            config: BaseSplitStepConfig,
    ) -> Output(train=DataArtifact,
                test=DataArtifact,
                validation=DataArtifact):
        """ hmmm """
