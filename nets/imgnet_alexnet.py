import torch
import torch.nn as nn
import torch.nn.init as init

from utils.quan_util import *


class AlexNet(nn.Module):
  def __init__(self, num_classes=1000):
    super(AlexNet, self).__init__()
    self.features = nn.Sequential(
      nn.Conv2d(3, 96, kernel_size=11, stride=4, padding=2),
      nn.BatchNorm2d(96),
      nn.ReLU(inplace=True),
      nn.MaxPool2d(kernel_size=3, stride=2),

      nn.Conv2d(96, 256, kernel_size=5, padding=2),
      nn.BatchNorm2d(256),
      nn.ReLU(inplace=True),
      nn.MaxPool2d(kernel_size=3, stride=2),

      nn.Conv2d(256, 384, kernel_size=3, padding=1),
      nn.ReLU(inplace=True),

      nn.Conv2d(384, 384, kernel_size=3, padding=1),
      nn.ReLU(inplace=True),

      nn.Conv2d(384, 256, kernel_size=3, padding=1),
      nn.ReLU(inplace=True),
      nn.MaxPool2d(kernel_size=3, stride=2),
    )
    self.classifier = nn.Sequential(
      nn.Linear(256 * 6 * 6, 4096),
      nn.ReLU(inplace=True),
      nn.Linear(4096, 4096),
      nn.ReLU(inplace=True),
      nn.Linear(4096, num_classes),
    )

    for m in self.modules():
      if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
        init.xavier_normal_(m.weight.data)

  def forward(self, x):
    x = self.features(x)
    x = x.view(x.size(0), 256 * 6 * 6)
    x = self.classifier(x)
    return x


class AlexNet_Q(nn.Module):
  def __init__(self, num_classes=1000):
    super(AlexNet_Q, self).__init__()
    self.Conv2d = conv2d_Q_fn(w_bit=1, order=2)
    self.Linear = linear_Q_fn(w_bit=1, order=2)
    self.features = nn.Sequential(
      nn.Conv2d(3, 96, kernel_size=11, stride=4, padding=2),
      nn.BatchNorm2d(96),
      nn.ReLU(inplace=True),
      nn.MaxPool2d(kernel_size=3, stride=2),

      self.Conv2d(96, 256, kernel_size=5, padding=2),
      nn.BatchNorm2d(256),
      nn.ReLU(inplace=True),
      nn.MaxPool2d(kernel_size=3, stride=2),

      self.Conv2d(256, 384, kernel_size=3, padding=1),
      nn.ReLU(inplace=True),

      self.Conv2d(384, 384, kernel_size=3, padding=1),
      nn.ReLU(inplace=True),

      self.Conv2d(384, 256, kernel_size=3, padding=1),
      nn.ReLU(inplace=True),
      nn.MaxPool2d(kernel_size=3, stride=2),
    )
    self.classifier = nn.Sequential(
      self.Linear(256 * 6 * 6, 4096),
      nn.ReLU(inplace=True),
      self.Linear(4096, 4096),
      nn.ReLU(inplace=True),
      nn.Linear(4096, num_classes),
    )

    for m in self.modules():
      if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
        init.xavier_normal_(m.weight.data)

  def forward(self, x):
    x = self.features(x)
    x = x.view(x.size(0), 256 * 6 * 6)
    x = self.classifier(x)
    return x


if __name__ == '__main__':
  from torch.autograd import Variable

  features = []


  def hook(self, input, output):
    print(output.data.cpu().numpy().shape)
    features.append(output.data.cpu().numpy())


  net = AlexNet_Q()
  net.train()

  for w in net.named_parameters():
    print(w[0])

  for m in net.modules():
    m.register_forward_hook(hook)

  y = net(Variable(torch.randn(1, 3, 224, 224)))
  print(y.size())
