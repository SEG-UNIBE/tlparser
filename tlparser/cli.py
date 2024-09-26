import click
import os
import json
import csv
import shutil
import pandas as pd
import matplotlib.pyplot as plt

from tlparser.config import Configuration
from tlparser.utils import Utils

# Default working directory name
DEFAULT_WD = "workingdir"

def get_working_directory():
    """Get or create the working directory"""
    # Create the path for the working directory in the same folder as the script
    script_location = os.path.dirname(os.path.abspath(__file__))
    working_dir = os.path.join(script_location, DEFAULT_WD)

    # Check if the working directory exists
    if not os.path.exists(working_dir):
        # Create the working directory and notify the user
        os.makedirs(working_dir, exist_ok=True)
        click.echo(f"Working directory ['{working_dir}'] has been created.")
    else:
        click.echo(f"Using existing working directory: [{working_dir}]")

    return working_dir

@click.group()
@click.version_option()
def cli():
    "Temporal Logic Parser"

@cli.command(name="digest")
@click.argument("json_file", type=click.Path(exists=True))
def digest_file(json_file):
    """Processes the JSON file and outputs a CSV"""
    working_dir = get_working_directory()
    config = Configuration(
        file_data_in=json_file, 
        folder_data_out=working_dir)
    util = Utils(config)
    formulas = util.read_formulas_from_json()
    util.write_to_excel(formulas)
    
    click.echo(f"Processed {json_file} and saved results to {csv_file_path}")

@cli.command(name="visualize")
@click.argument("csv_file", type=click.Path(exists=True))
def visualize_data(csv_file):
    """Creates a PDF plot from the CSV file"""
    working_dir = get_working_directory()

    # Read the CSV file
    data = pd.read_csv(csv_file)

    # Simple visualization: Plotting a bar chart of the first two columns
    plt.figure(figsize=(10, 6))
    data.plot(kind='bar', x=data.columns[0], y=data.columns[1])
    
    # Save the plot in a subfolder 'plots' in the working directory
    plots_folder = os.path.join(working_dir, "plots")
    os.makedirs(plots_folder, exist_ok=True)
    
    pdf_path = os.path.join(plots_folder, "visualization.pdf")
    plt.savefig(pdf_path)
    click.echo(f"Visualization saved as {pdf_path}")

@cli.command(name="cleanup")
def cleanup_folder():
    """Empties the working folder except JSON files"""
    working_dir = get_working_directory()
    files_to_delete = [
        f for f in os.listdir(working_dir)
        if not f.endswith('.json')
    ]
    file_count = len(files_to_delete)

    if file_count == 0:
        click.echo("No files to clean up in the working directory.")
        return
    
    # Prompt user for confirmation
    if click.confirm(f"Execution of this command will remove {file_count} files inside of '{working_dir}'." +
                     "\nDo you want to proceed?", default=False):
        for filename in files_to_delete:
            file_path = os.path.join(working_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                click.echo(f'Failed to delete {file_path}. Reason: {e}')
        
        click.echo(f"Cleaned up {file_count} files from the working directory: {working_dir}")
    else:
        click.echo("Cleanup operation aborted.")