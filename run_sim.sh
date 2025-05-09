#!/bin/bash -x

# Check if all required arguments are provided
if [ $# -lt 3 ]; then
    echo "Error: Please provide all required arguments"
    echo "Usage: $0 <directory_path> <num_simulations> <num_epochs>"
    exit 1
fi

# Assign arguments to variables
DIRECTORY="$1"
NUM_SIMULATIONS="$2"
NUM_EPOCHS="$3"

# Check if the provided path is a directory
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: '$DIRECTORY' is not a valid directory"
    exit 1
fi

# Validate that simulations and epochs are positive integers
if ! [[ "$NUM_SIMULATIONS" =~ ^[0-9]+$ ]] || [ "$NUM_SIMULATIONS" -lt 1 ]; then
    echo "Error: Number of simulations must be a positive integer"
    exit 1
fi

if ! [[ "$NUM_EPOCHS" =~ ^[0-9]+$ ]] || [ "$NUM_EPOCHS" -lt 1 ]; then
    echo "Error: Number of epochs must be a positive integer"
    exit 1
fi

# Find and list all yml files in the specified directory
echo "Listing all YAML files in $DIRECTORY:"
yml_files=$(find "$DIRECTORY" -type f \( -name "*.yml" -o -name "*.yaml" \))

echo "Will run $NUM_SIMULATIONS simulations with $NUM_EPOCHS epochs each"

source ./bin/activate

for k in $yml_files
do
    # Extract the base name of the file without the extension
    base_name=$(basename "$k" .yml)
    
    # Create a directory for the simulation results
    mkdir -p "$DIRECTORY/$base_name"
    
    # Run the simulation command with the specified parameters
    echo "Running simulation for $k..."

    for((I=1000;I<(($NUM_SIMULATIONS+1000));I=I+1))
      do ./ppS-cli.py --epochs $NUM_EPOCHS --batch -f $k | tee "$DIRECTORY/${base_name}/${base_name}-${I}.csv"
    done
    ~/.venvs/yapps/bin/python3 ./run_stats.py --num-epochs $NUM_EPOCHS -o "${DIRECTORY}/${base_name}" ${DIRECTORY}/${base_name}/${base_name}-*.csv
        
    echo "Simulation completed for $k. Results saved in $DIRECTORY/$base_name"
done