import torch.nn as nn
import torchvision.models as models


class ResNet18:
    def __init__(self, in_channels_1, number_of_classes):
        self.number_of_classes = number_of_classes
        self.model = models.resnet18()
        # wandb.log({"Model size": str(self.model)})
        self.model.conv1 = nn.Conv2d(
            in_channels_1, 64, kernel_size=7, stride=2, padding=3, bias=False
        )
        pretrained_bool = True
        if pretrained_bool:
            for param in self.model.parameters():
                param.requires_grad = False

        # Adding two fully connected layers
        self.model.fc = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, self.number_of_classes),
        )


class ResNet(nn.Module):
    def __init__(self, in_channels_1, number_of_classes):
        super(ResNet, self).__init__()

        # First stream of ResNet()
        self.res_net_1 = ResNet18(in_channels_1, number_of_classes).model

    def forward(self, x1):
        # Process modality 1 input
        x = self.res_net_1(x1)

        return x