import time
import logging
import os
from src.config import LOGS_DIR, TRAINING_INTERVAL_SEC
from hardcore_training import hardcore_training

# Setup a specific log for the continuous process
logging.basicConfig(
    filename=str(LOGS_DIR / "continuous_process.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Continuous Training Process Started.")
    print("Continuous Training Process Started. You can safely disconnect.")

    iteration = 1
    while True:
        try:
            logging.info(f"Starting Training Iteration {iteration}")
            hardcore_training()
            logging.info(f"Iteration {iteration} complete. Sleeping for {TRAINING_INTERVAL_SEC}s...")
            time.sleep(TRAINING_INTERVAL_SEC)
            iteration += 1
        except Exception as e:
            logging.error(f"Error in continuous training loop: {e}")
            time.sleep(60) # Wait a minute before retrying on error

if __name__ == "__main__":
    main()
