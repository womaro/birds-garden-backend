#pack_for_cvat.py - pakuje labelki YOLO do ZIP-a do importu w CVAT (YOLO 1.1).
#Uzycie: python tools/pack_for_cvat.py --src ~/Desktop/grab_dedup --out ~/Desktop/cvat_preann.zip""
import argparse, glob, os, zipfile

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--out", default=os.path.expanduser("~/Desktop/cvat_preann.zip"))
    a = p.parse_args()
    src = os.path.expanduser(a.src); out = os.path.expanduser(a.out)
    txts = sorted(glob.glob(os.path.join(src, "*.txt")))
    if not txts:
        print("brak .txt w", src, "- najpierw preannotate.py"); return
    names = [os.path.splitext(os.path.basename(t))[0] for t in txts]
    train_lines = [f"data/obj_train_data/{n}.jpg" for n in names]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("obj.names", "bird\n")
        z.writestr("obj.data", "classes = 1\ntrain = data/train.txt\nnames = data/obj.names\nbackup = backup/\n")
        z.writestr("train.txt", "\n".join(train_lines) + "\n")
        for t in txts:
            z.write(t, f"obj_train_data/{os.path.basename(t)}")
    print(f"gotowe: {out}\n  labelek: {len(txts)}")
    print("\nImport w CVAT: Task -> Actions -> Upload annotations -> 'YOLO 1.1' -> ten ZIP")

if __name__ == "__main__":
    main()