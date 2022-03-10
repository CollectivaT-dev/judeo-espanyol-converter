import pandas as pd
import main as m
from tqdm import tqdm
import argparse
import sys
import os


def get_dataset(url):
    text = []
    with open(url, 'r', encoding="utf-8") as lines:
        for line in lines:
            text.append(line.replace("\n", ""))
    return text

def find_all(name, path):
    result = []
    counter = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.find(name) != -1:
                text = get_dataset(path+file)
                counter = counter + len(text)
                result.append(os.path.join(root, name))
    return len(result), counter


def main():
    parser = argparse.ArgumentParser("translate Spanish <> Judeo-Spanish (Ladino)")
    parser.add_argument("-d", "--lad_dic", help="Dictionary root.", default=None, required=True)
    parser.add_argument("-s1", "--input_esp", help="Sentence segmented Spanish text file to translate",
                        default=None)
    parser.add_argument("-s2", "--input_2", help="Sentence segmented other language text file",
                        default=None)
    parser.add_argument("-n", "--language", help="second language name",
                        default=None)
    parser.add_argument("-o", "--output", help="Output path", default=None)
    args = parser.parse_args()

    root_dic = args.lad_dic
    root_dataset_1 = args.input_esp
    root_dataset_2 = args.input_2
    root_translate = args.output
    language = args.language

    if not args.lad_dic:
        print("ERROR: No dictionary given.")
        sys.exit()

    if not os.path.exists(root_translate):
        print("Creating directory")
        os.makedirs(root_translate)

    outfilename = os.path.basename(root_dataset_1)
    files_n, counter = find_all(outfilename+"_", root_translate)
    outfilepath = os.path.join(root_translate, outfilename+"_"+str(files_n+1) + ".csv")
    print("Output to:", outfilepath)
    print("Reading dictionary", args.lad_dic)
    dic = []

    with open(root_dic, 'r', encoding="utf-8") as lines:
        for line in lines:
            p = {"src": line.split(";")[0], "target": line.split(";")[1]}
            dic.append(p)

    sentences_es = get_dataset(root_dataset_1)
    sentences_en = get_dataset(root_dataset_2)

    name = root_dataset_2.split("/")[-1]
    name = name.split(".")[0]

    en = []
    es = []
    la = []
    s = []
    flag = 0
    print("Now translate...")
    count = 1
    translate_iter = zip(sentences_es, sentences_en)
    total = min(len(sentences_es), len(sentences_en))
    with tqdm(total=total) as pbar:
        for a, b in translate_iter:
            if count > counter:
                en.append(b)
                es.append(a)
                la.append(m.translate(a, dic))
                s.append(name)
                flag = flag + 1
                if flag % 500 == 0:
                    p = {'Source': s, language: en, 'Spanish': es, 'Ladino': la}
                    df_1 = pd.DataFrame(p)
                    df_1.to_csv(outfilepath, sep='\t', index=False)
                    print("Save...")
            count = count + 1
            pbar.update(1)
        pbar.close()
    
    p = {'Source': s, language: en, 'Spanish': es, 'Ladino': la}
    df_1 = pd.DataFrame(p)
    df_1.to_csv(outfilepath, sep='\t', index=False)

    print("Finished...", outfilepath)

if __name__ == '__main__':
    main()
