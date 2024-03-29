import torch

# Import models

from master_thesis_benge.self_supervised_learning.model.evaluation.dual_resnet import (
    #DualResNet,
    TripleResNet
)

from master_thesis_benge.self_supervised_learning.model.training.projection_head import AddResNetProjection

# Import constants
from master_thesis_benge.self_supervised_learning.config.constants import (
    Task,
    NUMBER_OF_CLASSES_KEY,
    EPOCHS_KEY,
    LEARNING_RATE_KEY,
    BATCH_SIZE_KEY,
    OPTIMIZER_KEY,
    SCHEDULER_KEY,
    LOSS_KEY,
    SEED_KEY,
    SCHEDULER_MAX_NUMBER_ITERATIONS_KEY,
    SCHEDULER_MIN_LR_KEY,
    SAVE_MODEL_KEY,
    MODEL_KEY,
    MODALITIES_LABEL_KEY,
    MODALITIES_KEY,
    MULTICLASS_ONE_HOT_LABEL_INDEX_KEY,
    ESA_WORLD_COVER_INDEX_KEY,
    MODALITIES_KEY,
    METRICS_KEY,
    SENTINEL_2_INDEX_KEY,
    DATALOADER_TRAIN_FILE_KEY,
    DATALOADER_VALIDATION_FILE_KEY,
    TASK_KEY,
    FEATURE_DIMENSION_KEY,
    EMEDDING_SIZE_KEY,
    PROJECTION_HEAD_KEY
)

from master_thesis_benge.self_supervised_learning.metrics.classification_utils import (
    ClassificationUtils,
)

from remote_sensing_core.constants import Bands

from remote_sensing_core.transforms.ffcv.min_max_scaler import MinMaxScaler
from remote_sensing_core.transforms.ffcv.clipping import Clipping
from remote_sensing_core.transforms.ffcv.channel_selector import ChannelSelector
from remote_sensing_core.transforms.ffcv.convert import Convert
from remote_sensing_core.transforms.ffcv.esa_world_cover_transform import EsaWorldCoverTransform
from remote_sensing_core.transforms.ffcv.blow_up import BlowUp
from remote_sensing_core.transforms.ffcv.min_max_scaler import MinMaxScaler
from remote_sensing_core.transforms.ffcv.era5_temperature_s2_transform import Era5TemperatureS2Transform
from remote_sensing_core.transforms.ffcv.expand_dimension import ExpandDimension

from ffcv.transforms import ToTensor, ToDevice
from ffcv.fields.decoders import NDArrayDecoder, FloatDecoder, IntDecoder

evaluation_config_classification_landuse_multilabel = {
    "task": {
        TASK_KEY: Task.SSL_CLASSIFICATION_LANDUSE_MULTILABEL.value
    },
    "model": {
        MODEL_KEY: TripleResNet,
        NUMBER_OF_CLASSES_KEY: 11,
    },
    "training": {
        MODALITIES_KEY: {
            MODALITIES_LABEL_KEY: MULTICLASS_ONE_HOT_LABEL_INDEX_KEY,
        },
        #DATALOADER_TRAIN_FILE_KEY: '/raid/remote_sensing/ben-ge/ffcv/ben-ge-60-delta-multilabel-train-1-percent.beton',
        DATALOADER_VALIDATION_FILE_KEY: '/ds2/remote_sensing/ben-ge/ffcv/ben-ge-20-multi-label-ewc-validation.beton',
        EPOCHS_KEY: 20,
        LEARNING_RATE_KEY: 0.001,
        BATCH_SIZE_KEY: 32,
        OPTIMIZER_KEY: torch.optim.Adam,
        SCHEDULER_KEY: torch.optim.lr_scheduler.CosineAnnealingLR,
        LOSS_KEY: torch.nn.BCEWithLogitsLoss(),
        #SEED_KEY: 42,
        SCHEDULER_MAX_NUMBER_ITERATIONS_KEY: 20,
        SCHEDULER_MIN_LR_KEY: 0,
        FEATURE_DIMENSION_KEY: 512,
        EMEDDING_SIZE_KEY: 128,
        PROJECTION_HEAD_KEY: AddResNetProjection,
    },
    "metrics": {METRICS_KEY: ClassificationUtils},
    "other": {
        SAVE_MODEL_KEY: False,
    },
    "pipelines": {
        'climate_zone': [FloatDecoder(), MinMaxScaler(maximum_value=29, minimum_value=0, interval_max=1, interval_min=0), BlowUp([1,120,120]), Convert('float32'), ToTensor(), ToDevice(device = torch.device('cuda'))],
        #'elevation_differ': [FloatDecoder(), ToTensor(), ToDevice(device)],
        'era_5': [NDArrayDecoder(), Era5TemperatureS2Transform(batch_size=32), BlowUp([1,120,120]), Convert('float32'), ToTensor(), ToDevice(device = torch.device('cuda'))],
        'esa_worldcover': [NDArrayDecoder(), EsaWorldCoverTransform(10,1), ExpandDimension(), ToTensor(), ToDevice(device = torch.device('cuda'))],
        'glo_30_dem': [NDArrayDecoder(), ChannelSelector([0]), ToTensor(), ToDevice(device = torch.device('cuda'))],
        #'multiclass_numer': [NDArrayDecoder(), ToTensor(), ToDevice(device)],
        'multiclass_one_h': [ToTensor(), ToDevice(device = torch.device('cuda'))],
        'season_s1': [FloatDecoder(), BlowUp([1,120,120]), Convert('float32'), ToTensor(), ToDevice(device = torch.device('cuda'))],
        'season_s2': [FloatDecoder(), BlowUp([1,120,120]), Convert('float32'), ToTensor(), ToDevice(device = torch.device('cuda'))],
        'sentinel_1': [NDArrayDecoder(), ToTensor(), ToDevice(device = torch.device('cuda'))],
        'sentinel_2': [NDArrayDecoder(), Clipping([0, 10_000]), ChannelSelector([7, 3, 2, 1]), ToTensor(), ToDevice(device=torch.device('cuda'))],
    },
}


def get_data_set_files(size: str):
    train_file = f'/ds2/remote_sensing/ben-ge/ffcv/ben-ge-{str(size)}-train.beton'
    validation_file = f'/ds2/remote_sensing/ben-ge/ffcv/ben-ge-{str(size)}-validation.beton'
    return train_file, validation_file
