# Spec2017_Gem5_SE_setup
Help files to set up SPEC 2017 benchmarks to run with Gem5 in SE mode

1. Install spec 2017 files from the ISO file or extract from the available zipped files
- Few helpful commands:  
 mkdir -p ~/spec2017  
 bsdtar -C ~/spec2017 -xf cpu2017-1.1.9.iso  
 In the spec2017 folder and execute ./install.sh it will generate benchspec and misc folder  
 ./install.sh -d\<directory to install\>

3. Choose a config file appropriate to the ISA used in the Gem5 build. Here, I have used the linux_x86 config to generate benchmark exe files

4. Set up binaries and run folders with  
runcpu --config=linux_x86.cfg --action=validate --tune=base specspeed specrate

5. Create setup files as given in the reference and customise
-References:  
https://zhuanlan.zhihu.com/p/607111813#ref_4  
https://seanzw.github.io/posts/gem5-spec2017/  

6. A sample automation script to run multiple benchmarks with multiple configurations is added, modify paths wherever necessary.
