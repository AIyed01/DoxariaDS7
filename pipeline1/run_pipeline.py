import os
from data_loader import load_data
from preprocess import create_generators
from train import build_model, train_model

# Get absolute path to scream if anything is wrong
dataset_dir = os.path.abspath(os.getenv("DATASET_DIR"))
if not dataset_dir:
    raise RuntimeError("🔥 DATASET_DIR environment variable not set - check your GitHub Secrets")

print(f"🔄 Using dataset directory: {dataset_dir}")

train_folder = os.path.join(dataset_dir, "train")
test_folder = os.path.join(dataset_dir, "test")

# Nuclear verification
if not os.path.exists(train_folder):
    raise FileNotFoundError(f"💥 TRAIN FOLDER MISSING: {train_folder}")
if not os.path.exists(test_folder):
    raise FileNotFoundError(f"💥 TEST FOLDER MISSING: {test_folder}")

print("✅ Found both train and test folders")

# Load data with verification
X_train, y_train, X_test, y_test = load_data(train_folder, test_folder)
if len(X_train) == 0:
    raise RuntimeError("💢 Loaded ZERO training samples - check your data structure")
if len(X_test) == 0:
    raise RuntimeError("💢 Loaded ZERO test samples - check your data structure")

print(f"📊 Loaded {len(X_train)} training and {len(X_test)} test samples")

# Rest of your pipeline...
train_gen, val_gen = create_generators(X_train, y_train, X_test, y_test)
model = build_model()
train_model(model, train_gen, val_gen)