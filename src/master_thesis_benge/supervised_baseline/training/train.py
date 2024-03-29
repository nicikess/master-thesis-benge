from tqdm import tqdm
import torch.nn as nn
import torch
import os

from master_thesis_benge.supervised_baseline.config.constants import (
    TRAINING_CONFIG_KEY,
    OPTIMIZER_KEY,
    LEARNING_RATE_KEY,
    SCHEDULER_KEY,
    SCHEDULER_MAX_NUMBER_ITERATIONS_KEY,
    SCHEDULER_MIN_LR_KEY,
    EPOCHS_KEY,
    LOSS_KEY,
    MODEL_CONFIG_KEY,
    MODALITIES_KEY,
    MODALITIES_LABEL_KEY,
    NUMBER_OF_CLASSES_KEY,
    OTHER_CONFIG_KEY,
    SAVE_MODEL_KEY
)


class Train:
    def __init__(self, model, train_dl, validation_dl, metrics, wandb, device, config, task, modalities):
        self.model = model
        self.train_dl = train_dl
        self.validation_dl = validation_dl
        self.metrics = metrics
        self.wandb = wandb
        self.device = device
        self.config = config
        self.task = task
        self.modalities = modalities

        # Initialize optimizer and scheduler
        self.optimizer = config[TRAINING_CONFIG_KEY][OPTIMIZER_KEY](
            model.parameters(), lr=config[TRAINING_CONFIG_KEY][LEARNING_RATE_KEY]
        )
        
        self.scheduler = config[TRAINING_CONFIG_KEY][SCHEDULER_KEY](
            self.optimizer,
            T_max=config[TRAINING_CONFIG_KEY][SCHEDULER_MAX_NUMBER_ITERATIONS_KEY],
            eta_min=config[TRAINING_CONFIG_KEY][SCHEDULER_MIN_LR_KEY],
        )
        

    def train(self):
        # Move the model to the GPU
        self.model.to(self.device)

        # Init metrics

        self.metrics = self.metrics(
            self.wandb,
            self.device,
            number_of_classes=self.config[MODEL_CONFIG_KEY][NUMBER_OF_CLASSES_KEY],
            task=self.task,
        )

        # For every epoch
        for epoch in range(self.config[TRAINING_CONFIG_KEY][EPOCHS_KEY]):

            print("Task: "+str(self.task))

            progress = tqdm(
                enumerate(self.train_dl), desc="Train Loss: ", total=len(self.train_dl)
            )

            # Specify you are in training mode
            self.model.train()

            # Set metrics to 0
            self.metrics.reset_epoch_train_metrics()

            for i, (ben_ge_data) in progress:

                # Create forward data (remove label from dict)
                ben_ge_data_forward = {
                    key: ben_ge_data[key]
                    for key in self.modalities
                }

                # Rename keys
                ben_ge_data_forward = {'x{}'.format(i+1): value for i, (key, value) in enumerate(ben_ge_data_forward.items())}

                output = self.model(**ben_ge_data_forward)

                label = ben_ge_data[
                    self.config[TRAINING_CONFIG_KEY][MODALITIES_KEY][
                        MODALITIES_LABEL_KEY
                    ]
                ].to(self.device)

                # Compute the loss
                loss = self.metrics.calculate_loss(self.config[TRAINING_CONFIG_KEY][LOSS_KEY], output, label)

                # Clear the gradients
                self.optimizer.zero_grad()

                # Calculate gradients
                loss.backward()

                # Update Weights
                self.optimizer.step()

                # Calculate batch train metrics
                self.metrics.log_batch_train_metrics(loss, output, label, progress, epoch)

            self.scheduler.step()

            # Calculate epoch train metrics
            self.metrics.log_epoch_train_metrics(len(self.train_dl), scheduler=self.scheduler)

            progress = tqdm(
                enumerate(self.validation_dl),
                desc="val Loss: ",
                total=len(self.validation_dl),
                position=0,
                leave=True,
            )

            # Specify you are in evaluation mode
            self.model.eval()

            # Deactivate autograd engine (no backpropagation allowed)
            with torch.no_grad():
                # Set validation metrics to 0
                self.metrics.reset_epoch_validation_metrics()

                for i, (ben_ge_data) in progress:

                    # Create forward data (remove label from dict)
                    ben_ge_data_forward = {
                        key: ben_ge_data[key]
                        for key in self.modalities
                    }

                    # Rename keys
                    ben_ge_data_forward = {'x{}'.format(i + 1): value for i, (key, value) in
                                           enumerate(ben_ge_data_forward.items())}

                    # Make a forward pass
                    output = self.model(**ben_ge_data_forward)

                    label = ben_ge_data[
                        self.config[TRAINING_CONFIG_KEY][MODALITIES_KEY][
                            MODALITIES_LABEL_KEY
                        ]
                    ].to(self.device)

                    # Calculate batch validation metrics
                    self.metrics.log_batch_validation_metrics(output, label)

                # Calculate epoch validation metrics
                self.metrics.log_epoch_validation_metrics(len(self.validation_dl))


            print("Epoch: " + str(epoch))
            if self.config[OTHER_CONFIG_KEY][SAVE_MODEL_KEY]:
                sweep_id = str(self.wandb.run.sweep_id)
                save_weights_path = "saved_models/" + sweep_id

                if not os.path.exists(save_weights_path):
                    os.makedirs(save_weights_path)
                else:
                    print("Directory already exists:", save_weights_path)

                file_path = save_weights_path + '/state_dict_epoch_' + str(epoch) + '_.pt'
                if not os.path.exists(file_path):
                    torch.save(self.model.state_dict(), file_path)
                else:
                    print("File already exists:", file_path)
