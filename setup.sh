# CLONE REPOSITORY
git clone https://github.com/AstraBert/SupaSeqs
cd SupaSeqs

# INSTALL supabase
npm i supabase

# CREATE YOUR SUPABASE INSTANCE
npx supabase init

# START YOUR SUPABASE INSTANCE
npx supabase start

# RETRIEVE THE CONNECTION STRING
npx supabase status
## |_ Use DB URL as connection string
## |_ Use STUDIO URL as a way to access the dashboard

# CREATE A VIRUAL ENVIRONMENT...
python3 -m venv apienv

# ...AND ACTIVATE IT!
source apienv/bin/activate

# INSTALL THE REQUIRED PACKAGES
python3 -m pip install -r requirements.txt

# AND THE START THE APPLICATION!
cd scripts
python3 -m fastapi dev

# You'll find examples on how to use the application in the example folder!
