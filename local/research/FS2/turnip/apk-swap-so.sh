set -e
F=/home/brad/fs2; N=$1; SO=$2
mkdir -p $F/jniLibs-$N/arm64-v8a
cp /home/brad/vr2d/jniLibs/arm64-v8a/libhardware.so $F/jniLibs-$N/arm64-v8a/
cp $SO $F/jniLibs-$N/arm64-v8a/libvulkan_freedreno.so
JNILIBS=$F/jniLibs-$N $F/build-jni.sh > $F/build-$N.log 2>&1
cd $F/PS2Recomp/android/app/build/outputs/apk/release && cp app-release.apk $F/app-release-$N.apk
python3 -c "
import zipfile,hashlib
z=zipfile.ZipFile('$F/app-release-$N.apk')
for n in ('lib/arm64-v8a/libvulkan_freedreno.so','lib/arm64-v8a/libhardware.so','lib/arm64-v8a/libps2EntryRunner.so'):
    print(n, hashlib.sha256(z.read(n)).hexdigest())
"
sha256sum $F/app-release-$N.apk; grep "BUILD" $F/build-$N.log
