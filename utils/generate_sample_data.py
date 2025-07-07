import json
import os
from data_generator import DataGenerator


def main():
    generator = DataGenerator(seed=42)
    
    print("Generating sample data...")
    dataset = generator.generate_test_dataset()
    
    os.makedirs("../data/sample_tickets", exist_ok=True)
    os.makedirs("../data/knowledge_base", exist_ok=True)
    os.makedirs("../data/customer_profiles", exist_ok=True)
    
    with open("../data/sample_tickets/tickets.json", "w") as f:
        json.dump(dataset["tickets"], f, indent=2)
    print(f"Generated {len(dataset['tickets'])} sample tickets")
    
    with open("../data/knowledge_base/articles.json", "w") as f:
        json.dump(dataset["knowledge_base"], f, indent=2)
    print(f"Generated {len(dataset['knowledge_base'])} knowledge base articles")
    
    with open("../data/customer_profiles/profiles.json", "w") as f:
        json.dump(dataset["customer_profiles"], f, indent=2)
    print(f"Generated {len(dataset['customer_profiles'])} customer profiles")
    
    with open("../data/ground_truth.json", "w") as f:
        json.dump(dataset["ground_truth"], f, indent=2)
    print(f"Generated ground truth for {len(dataset['ground_truth'])} tickets")
    
    with open("../data/dataset_metadata.json", "w") as f:
        json.dump(dataset["metadata"], f, indent=2)
    
    print("\nSample data generation complete!")
    print(f"Data saved in: customer-support-agent/data/")


if __name__ == "__main__":
    main()