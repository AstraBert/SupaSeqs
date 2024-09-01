<h1 align="center">SupaSeqs</h1>
<h2 align="center">Basically BLAST written in PostgreSQL😉</h2>


<div align="center">
    <img src="https://img.shields.io/github/languages/top/AstraBert/SupaSeqs" alt="GitHub top language">
   <img src="https://img.shields.io/github/commit-activity/t/AstraBert/SupaSeqs" alt="GitHub commit activity">
   <img src="https://img.shields.io/badge/Status-stable_beta-green" alt="Static Badge">
   <img src="https://img.shields.io/badge/Release-v0.0_beta.0-purple" alt="Static Badge">
   <img src="https://img.shields.io/badge/Supported_platforms-Windows/POSIX-brown" alt="Static Badge">
   <br>
   <br>
   <div>
        <img src="./scripts/static/favicon.png" alt="Logo" align="center">
   </div>
   <br>
   <br>
</div>

**SupaSeqs** is a tool that can be used to manage DNA sequences databases locally, thanks to the PostgreSQL implementation offered by [*Supabase*](https://supabase.com/).

It leverages PostgreSQL as backend database manager, kmer-based vectorization and vector search to mimic the functionalities of BLAST. 

### 1. Installation 

If you are working in a Linux environment, you may want to just download/copy [setup.sh](./setup.sh) and launch it:

```bash
# Linux
wget https://raw.githubusercontent.com/AstraBert/SupaSeqs/main/scripts/setup.sh
bash setup.sh
```

### 1a. Pre-requirements

Make sure that your environment has:
- `git`
- `Node v18` or following
- `npm` and `npx`
- `python 3.10` or following
The installation process should work both on Windows and on Linux.

#### 1b. Environment setup

First of all, clone this repository:
```bash
# BOTH Windows and Linux
git clone https://github.com/AstraBert/SupaSeqs
cd SupaSeqs
```

Get the `supabase` command line executables:

```bash
# BOTH Windows and Linux
npm install supabase
```

Create and start a Supabase instance:

```bash
# BOTH Windows and Linux
npx supabase init
npx supabase start
```

Retrieve the connection string from the `DB URL` that will be printed after this command:

```bash
# BOTH Windows and Linux
npx supabase status
```

Create a virtual environment, activate it and install the necessary dependencies:

```bash
# Linux
python3 -m venv apienv
source apienv/bin/activate
python3 -m pip install -r requirements.txt
```

Or

```powershell
# Windows
python3 -m venv .\apienv
.\apienv\Scripts\activate  # For Command Prompt
# or
.\apienv\Activate.ps1  # For PowerShell
python3 -m pip install -r .\requirements.txt
```

#### 1c. Application start

Within the virtual environment, run:

```bash
# BOTH Windows and Linux
cd scripts
python3 -m fastapi dev 
```

If there are problems with the connection to the Supabase client, make sure to replace the connection string in [line of 16 `main.py`](./scripts/main.py#L16) with the one you found running `supabase status`.

### 2. How does it work

The application works as an API service, leveraging [FastAPI](https://fastapi.tiangolo.com/). The connection to Supabase is handled via a [`sqlalchemy`](https://docs.sqlalchemy.org/en/20/) implementation of a client which is similar to the one built in the [`vecs`](https://github.com/supabase/vecs) library.

The application accepts two request types:

1- **POST** - *Upload a sequence or a FASTA file*:
```bash
# Single sequence
curl -X POST "http://127.0.0.1:8000/seqs/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"sequence\":\"GGCAGAACCCAGGGCACCAGCACGCCGAAGGACCACCGCAGGCTGGCCAGCGCTCCACCCTCCCTGCACCACACCCTGCGAGCAAAAGGCAGCAGAAATGAAGAGCATTTACTTTGTGGCTGGATTGTTTGTAATGCTGGTACAAGGCAGCTGGCAACACCCACTTCAAGACACAGAGGAAAAACCCAGGTCTTTCTCAACTTCTCAAACAGACTTGCTTGATGATCCGGATCAGATGAATGAAGACAAGCGTCATTCACAGGGTACATTCACCAGTGACTACAGCAAGTTCCTCGACACCAGGCGTGCTCAAGACTTCTTGGATTGGCTGAAGAACACCAAGAGGAACAGGAATGAAAT\", \"description\": \"M57688.1 Octodon degus glucagon mRNA, complete cds\"}"
# FASTA file
curl -X POST "http://127.0.0.1:8000/seqs/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"sequence\": \"sequence.fasta\"}"
```
Each sequence gets vectorized with a 5-mer-based representation (a 1024-dim array), which is then uploaded to the `sequences` table on Supabase along with a description (if provided in the case of the single sequence, the headers of the sequences for those in a FASTA file) and the original sequence.

2- **GET** - *Search through the sequence database*
```bash
curl -X 'GET' 'http://localhost:8000/seqs/AACTTCTCAAACAGACTTGCTTGATGATCCGGATCAGATGAATGAAGACAAGCGTCATTCACAGGGTACATTCACCAGTGACTACAGCAAGTTCCTCGACACCAGGCGTGCTCAAGACTTCTTGGATTGGCTGAAGAACACCAAGAGGAACAGGAATGAAAT?limit=100&threshold=75' -H 'accept: application/json'
```

The query sequence gets vectorized and the database is searched: a number of sequences (specified with the _limit_ key, maximum is 1000) is returned if they are compliant with a similarity threshold (specified as a percentage value with the _threshold_ key); the typical response looks like this: 

```json
{"1":{"sequence":"GGCAGAACCCAGGGCACCAGCACGCCGAAGGACCACCGCAGGCTGGCCAGCGCTCCACCCTCCCTGCACCACACCCTGCGAGCAAAAGGCAGCAGAAATGAAGAGCATTTACTTTGTGGCTGGATTGTTTGTAATGCTGGTACAAGGCAGCTGGCAACACCCACTTCAAGACACAGAGGAAAAACCCAGGTCTTTCTCAACTTCTCAAACAGACTTGCTTGATGATCCGGATCAGATGAATGAAGACAAGCGTCATTCACAGGGTACATTCACCAGTGACTACAGCAAGTTCCTCGACACCAGGCGTGCTCAAGACTTCTTGGATTGGCTGAAGAACACCAAGAGGAACAGGAATGAAAT","description":"M57688.1 Octodon degus glucagon mRNA, complete cds","cos_dist":0.23987939711631145}}
```

This is accomplished thanks to a function called `match_page_sections` and defined as follows:

```sql
create or replace function public.match_page_sections (
  embedding vector(1024),
  match_threshold float,
  match_count int
)
returns setof public.sequences
language sql
as $$
  select *
  from public.sequences
  where public.sequences.embedding <=> embedding < 1 - match_threshold
  order by public.sequences.embedding <=> embedding asc
  limit least(match_count, 1000);
$$;
```

### 3. Contributions

Contributions are more than welcome! See [contribution guidelines](./CONTRIBUTING.md) for more information :)

### 4. Funding

If you found this project useful, please consider to [fund it](https://github.com/sponsors/AstraBert) and make it grow: let's support open-source together!😊

### 5. License and rights of usage

This project is provided under [MIT license](./LICENSE): it will always be open-source and free to use.

If you use this project, please cite the author: [Astra Clelia Bertelli](https://astrabert.vercel.app)








