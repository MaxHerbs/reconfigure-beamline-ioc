# bash run.sh configurations/master.yaml venv/bin/activate /scratch/$USER/p99-services/environment.sh

set -x

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Please provide the path to the virtual environment and the environment.sh file"
    exit 1
fi

for path in "$1" "$2" "$3"; do
    if [ ! -f "$path" ]; then
        echo "The path $path does not exist."
        exit 1
    fi
done

echo "config path: $1"
echo "venv path: $2"
echo "EC ENV PATH: $3"

source $2
source $3

eval $(ssh-agent)
ssh-add ~/.ssh/id_rsa

python main.py $1
