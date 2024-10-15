import argparse
import json
import os

from app.ai_services.openai_service import OpenAIService

def purge_assistants(config):
    print("Purging assistants...")
    # purge any orphaned assistants
    openai_service = OpenAIService(config['Keys']['OpenAI'], config)
    assistantList = openai_service.get_assistants()

    for assistant in assistantList:
        print(f"Deleting orphaned assistant {assistant.id}")
        openai_service.delete_assistant(assistant.id)

def main():

    # parse a configuration file
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    parser = argparse.ArgumentParser(description="Tools script for spooky season.")
    parser.add_argument('--purge_assistants', action='store_true', help='Purge assistants')
    
    args = parser.parse_args()
    
    if args.purge_assistants:
        purge_assistants(config)
    else:
        while True:
            print("\nTool Options Menu:")
            print("0: Exit")
            print("1: Purge assistants")
            # Add more options here as needed
            
            choice = input("Enter your choice: ")
            
            if choice == '0':
                print("Exiting...")
                break
            elif choice == '1':
                purge_assistants(config)
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
   

    