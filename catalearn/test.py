from tqdm import tqdm
import io


data = io.BytesIO(b'abcdefgabcdefgabcdefgabcdefgabcdefgabcdefgabcdefgabcdefg')

def gen(chunck_size):
    eof = False
    while not eof:
        chunck = data.read(chunck_size)
        yield chunck
        if len(chunck) <chunck_size:
            eof = True

for b in gen(10):
    print(len(b))
    print(b)