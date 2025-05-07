import mlflow
import mlflow.tensorflow
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow as tf
import os

# Use a relative path for MLflow tracking that works in any environment
mlflow.set_tracking_uri("./mlruns")

# Check for GPU availability
if tf.config.list_physical_devices('GPU'):
    print("GPU is available!")
else:
    print("GPU is not available!")

def build_model(input_shape=(224, 224, 3), num_classes=3):
    base_model = MobileNetV2(include_top=False, weights="imagenet", input_shape=input_shape)
    x = GlobalAveragePooling2D()(base_model.output)
    x = Dropout(0.3)(x)
    outputs = Dense(num_classes, activation="softmax")(x)
    model = Model(inputs=base_model.input, outputs=outputs)
    return model

def train_model(model, train_gen, val_gen, epochs=10):
    # Create mlruns directory if it doesn't exist
    os.makedirs("./mlruns", exist_ok=True)
    
    # Start MLflow run
    mlflow.start_run()

    # Log hyperparameters
    mlflow.log_param("epochs", epochs)
    mlflow.log_param("optimizer", "adam")
    mlflow.log_param("loss_function", "sparse_categorical_crossentropy")

    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    es = EarlyStopping(patience=3, restore_best_weights=True)

    # Train the model and log metrics
    history = model.fit(train_gen, validation_data=val_gen, epochs=epochs, callbacks=[es])

    # Log the accuracy as a metric
    val_accuracy = history.history["val_accuracy"][-1]
    mlflow.log_metric("validation_accuracy", val_accuracy)

    # Save the model and log it in MLflow
    model.save("model.h5")
    mlflow.tensorflow.log_model(model, "model")

    # End MLflow run
    mlflow.end_run()

    return model