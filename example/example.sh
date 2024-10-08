curl -X POST "http://127.0.0.1:8000/seqs/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"sequence\":\"GGCAGAACCCAGGGCACCAGCACGCCGAAGGACCACCGCAGGCTGGCCAGCGCTCCACCCTCCCTGCACCACACCCTGCGAGCAAAAGGCAGCAGAAATGAAGAGCATTTACTTTGTGGCTGGATTGTTTGTAATGCTGGTACAAGGCAGCTGGCAACACCCACTTCAAGACACAGAGGAAAAACCCAGGTCTTTCTCAACTTCTCAAACAGACTTGCTTGATGATCCGGATCAGATGAATGAAGACAAGCGTCATTCACAGGGTACATTCACCAGTGACTACAGCAAGTTCCTCGACACCAGGCGTGCTCAAGACTTCTTGGATTGGCTGAAGAACACCAAGAGGAACAGGAATGAAAT\", \"description\": \"M57688.1 Octodon degus glucagon mRNA, complete cds\"}"

curl -X POST "http://127.0.0.1:8000/seqs/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"sequence\": \"sequence.fasta\"}"

curl -X 'GET' 'http://localhost:8000/seqs/AACTTCTCAAACAGACTTGCTTGATGATCCGGATCAGATGAATGAAGACAAGCGTCATTCACAGGGTACATTCACCAGTGACTACAGCAAGTTCCTCGACACCAGGCGTGCTCAAGACTTCTTGGATTGGCTGAAGAACACCAAGAGGAACAGGAATGAAAT?limit=100&threshold=75' -H 'accept: application/json'

