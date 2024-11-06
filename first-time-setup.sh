set -x
echo "Running first time setup..."

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

git clone git@github.com:MaxHerbs/p99-services.git

echo "First time setup complete."
echo "To run the program, use the following command:"
echo "bash run.sh configurations/master.yaml venv/bin/activate p99-services/environment.sh"