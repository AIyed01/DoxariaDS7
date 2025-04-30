import os
from data_loader import load_data
from preprocess import create_generators
from train import build_model, train_model

# Define your dataset paths
dataset_dir = r"C:/Users/walid/Downloads/DSPI/data_doxaria/dataset"
train_folder = os.path.join(dataset_dir, "train")
test_folder = os.path.join(dataset_dir, "test")

# Load data
X_train, y_train, X_test, y_test = load_data(train_folder, test_folder)

# Create generators for training
train_gen, val_gen = create_generators(X_train, y_train, X_test, y_test)

# Build and train the model
model = build_model()
train_model(model, train_gen, val_gen)
