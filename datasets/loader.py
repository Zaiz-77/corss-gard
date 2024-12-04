import numpy as np
import torch
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

from datasets.office_dataset import Office31, OfficeHome

data_root = '/home/wangkai/handwrite/data'
cub_root = '/home/wangkai/crossgrad/data/CUB_200_2011'
office31_root = '/home/wangkai/handwrite/data/OFFICE31'
office_home_root = '/home/wangkai/handwrite/data/OfficeHome'


class MyLoader(DataLoader):
    def __init__(self, dataset, domain, **kwargs):
        super().__init__(dataset, **kwargs)
        self.domain = domain


def get_mnist_dataloader(batch_size=64, num_workers=8):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    train_dataset = datasets.MNIST(data_root, train=True, download=False, transform=transform)
    test_dataset = datasets.MNIST(data_root, train=False, download=False, transform=transform)
    print(f'Mnist Train: {len(train_dataset)}, Mnist Test: {len(test_dataset)}')

    train_loader = MyLoader(train_dataset, domain='mnist', batch_size=batch_size, shuffle=True, num_workers=num_workers)
    test_loader = MyLoader(test_dataset, domain='mnist', batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return train_loader, test_loader


def get_usps_dataloader(batch_size=64, num_workers=8):
    transform = transforms.Compose([
        transforms.Resize((28, 28)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    train_dataset = datasets.USPS(data_root, train=True, download=False, transform=transform)
    test_dataset = datasets.USPS(data_root, train=False, download=False, transform=transform)
    print(f'USPS Train: {len(train_dataset)}, USPS Test: {len(test_dataset)}')

    train_loader = MyLoader(train_dataset, domain='usps', batch_size=batch_size, shuffle=True, num_workers=num_workers)
    test_loader = MyLoader(test_dataset, domain='usps', batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return train_loader, test_loader


def get_office31_loaders(batch_size=64, num_workers=8, train_ratio=0.8):
    data_transforms = transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    domains = ['amazon', 'dslr', 'webcam']
    train_loaders = {}
    test_loaders = {}

    for domain in domains:
        dataset = Office31(office31_root, domain, data_transforms)
        train_size = int(len(dataset) * train_ratio)
        test_size = len(dataset) - train_size
        train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

        train_dataset.__class__.__name__ = dataset.__class__.__name__
        test_dataset.__class__.__name__ = dataset.__class__.__name__

        train_loaders[domain] = MyLoader(
            train_dataset,
            domain=domain,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True
        )

        test_loaders[domain] = MyLoader(
            test_dataset,
            domain=domain,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        )

        print(f"{domain.capitalize()} - Train: {train_size}, Test: {test_size}")

    return train_loaders, test_loaders


def get_office_home_loaders(batch_size=64, num_workers=8, train_ratio=0.8):
    data_transforms = transforms.Compose([
        transforms.Resize([256, 256]),
        transforms.RandomHorizontalFlip(),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    domains = ['Art', 'Clipart', 'Product', 'RealWorld']
    train_loaders = {}
    test_loaders = {}

    for domain in domains:
        dataset = OfficeHome(office_home_root, domain, data_transforms)

        train_size = int(len(dataset) * train_ratio)
        test_size = len(dataset) - train_size

        train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

        train_dataset.__class__.__name__ = dataset.__class__.__name__
        test_dataset.__class__.__name__ = dataset.__class__.__name__

        train_loaders[domain] = MyLoader(
            train_dataset,
            domain=domain,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True
        )

        test_loaders[domain] = MyLoader(
            test_dataset,
            domain=domain,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        )

        print(f"{domain.capitalize()} - Train: {train_size}, Test: {test_size}")

    return train_loaders, test_loaders


def show_batch_data(loader, save_name, mean=None, std=None, num_rows=8, num_cols=8, size=(15, 15)):
    images, labels = next(iter(loader))
    print(f'{save_name}: \n'
          f'Input Size: {images.shape}, Output Size: {labels.shape}')

    if mean is not None and std is not None:
        mean = torch.tensor(mean).view(3, 1, 1)
        std = torch.tensor(std).view(3, 1, 1)
        images = images * std + mean

    fig, axes = plt.subplots(num_rows, num_cols, figsize=size)

    for i, ax in enumerate(axes.flat):
        if i < len(images):
            if images.shape[1] == 3:
                img = images[i].permute(1, 2, 0).numpy()
                img = np.clip(img, 0, 1)
                ax.imshow(img)
            else:
                ax.imshow(images[i].squeeze(), cmap='gray')

            ax.set_title(f'Label: {labels[i].item()}', fontsize=10)
            ax.axis('off')

    plt.tight_layout()
    plt.savefig(f'{save_name}_data.png')
    plt.close()


if __name__ == '__main__':
    mnist_train, mnist_test = get_mnist_dataloader()
    usps_train, usps_test = get_usps_dataloader()
    office31_train, office31_test = get_office31_loaders()
    office_home_train, office_home_test = get_office_home_loaders()

    show_batch_data(mnist_train, 'mnist_train')
    show_batch_data(usps_train, 'usps_train')

    show_batch_data(office31_train['amazon'], '31_amazon_train', mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    show_batch_data(office31_train['dslr'], '31_dslr_train', mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    show_batch_data(office31_train['webcam'], '31_webcam_train', mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    show_batch_data(office_home_train['Art'], 'home_Art_train', mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    show_batch_data(office_home_train['Clipart'], 'home_Clipart_train', mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225])
    show_batch_data(office_home_train['Product'], 'home_Product_train', mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225])
    show_batch_data(office_home_train['RealWorld'], 'home_RealWorld_train', mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225])