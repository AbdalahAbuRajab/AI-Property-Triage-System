import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader


DATA_DIR = "dataset"
MODEL_OUTPUT_PATH = "room_condition_model.pth"
NUM_CLASSES = 6

ROOM_CLASSES = [
    "kitchen",
    "bathroom",
    "living_room",
    "bedroom",
    "exterior",
    "other"
]


def build_model():
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)

    for param in model.features.parameters():
        param.requires_grad = False

    in_features = model.classifier[1].in_features

    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 128),
        nn.ReLU(),
        nn.Linear(128, NUM_CLASSES)
    )

    return model


def train():
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    dataset = datasets.ImageFolder(DATA_DIR, transform=transform)

    dataloader = DataLoader(
        dataset,
        batch_size=8,
        shuffle=True
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = build_model()
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.Adam(
        model.classifier.parameters(),
        lr=0.001
    )

    epochs = 5

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in dataloader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        accuracy = correct / total if total > 0 else 0

        print(
            f"Epoch {epoch + 1}/{epochs} | "
            f"Loss: {running_loss:.4f} | "
            f"Accuracy: {accuracy:.2f}"
        )

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "classes": ROOM_CLASSES
        },
        MODEL_OUTPUT_PATH
    )

    print(f"Model saved to {MODEL_OUTPUT_PATH}")


if __name__ == "__main__":
    train()