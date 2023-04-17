from torch import nn
import numpy as np
import torch
import torchvision.models as models


class ResNet:
    def __init__(self, in_channels_1, number_of_classes):
        self.number_of_classes = number_of_classes
        self.model = models.resnet18()
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
        )


# Create the last convolution block
class LinearFC(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(LinearFC, self).__init__()
        self.fc = nn.Linear(in_channels, out_channels)

    def forward(self, x):
        return self.fc(x)


class DualResNet(nn.Module):
    def __init__(self, in_channels_1, in_channels_2, number_of_classes):
        super(DualResNet, self).__init__()

        # First stream of ResNet()
        self.res_net_1 = ResNet(in_channels_1, number_of_classes).model
        # Second stream of ResNet()
        self.res_net_2 = ResNet(in_channels_2, number_of_classes).model

        # TODO: Uncomment to test
        self.fc = LinearFC(2 * 256, number_of_classes)

    def forward(self, x1, x2):
        # Process modality 1 input
        x1 = self.res_net_1(x1)
        # Process modality 2 input
        x2 = self.res_net_2(x2)

        x = torch.cat([x1, x2], dim=1)

        x = self.fc(x)

        return x
