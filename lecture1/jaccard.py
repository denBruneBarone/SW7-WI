def jaccard(string1, string2):
    shingles1 = split_to_shingles(string1)
    shingles2 = split_to_shingles(string2)

    compare_shingles(shingles1, shingles2)
def split_to_shingles(string):
    shingles = []
    words = string.split()
    length = len(words)
    for i in range(length-2):
        shingles.append(words[i] + " " + words[i+1] + " " + words[i+2])
    return shingles


def compare_shingles(shingle1, shingle2):
    intersection_score = 0
    union_score = 0
    for shingle in shingle1:
        if shingle in shingle2:
            intersection_score += 1





    print(big_score / len(union))



if __name__ == '__main__':
    jaccard("do not worry about your difficulties in mathematics", "i would not worry about your difficulties you can easily learn what is needed")


