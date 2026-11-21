package de.universelab.sternfenster;
public final class ProjectionCheck {
    private static void close(double got, double expected, String name) {
        if (Math.abs(got-expected)>0.005) throw new AssertionError(name+": "+got+" vs "+expected);
    }
    public static void main(String[] args) {
        int cases=0;
        for(int az=0;az<360;az+=30) {
            for(int alt=0;alt<=90;alt+=15) {
                SkyProjection p=new SkyProjection(720,1200,az,alt,90);
                if(!p.horizontal(alt,az))throw new AssertionError("center rejected");
                close(p.x,360,"center x");close(p.y,600,"center y");cases++;
                if(alt<=75) {
                    if(!p.horizontal(alt+10,az))throw new AssertionError("up rejected");
                    close(p.x,360,"up x");close(p.y,600-1200.0*10/90,"up y");cases++;
                }
            }
        }
        SkyProjection p=new SkyProjection(900,900,0,0,90);
        if(p.horizontal(0,180))throw new AssertionError("antipode not rejected");
        p.horizontal(45,0);close(p.y,0,"top field edge");
        p.horizontal(0,45);close(p.x,900,"right field edge");
        p.horizontal(0,315);close(p.x,0,"left field edge");
        int[][] sizes={{900,900},{1500,2100},{1440,600},{400,1800},{280,110},{1,1},{0,-1},{Integer.MAX_VALUE,Integer.MAX_VALUE}};
        for(int[] input:sizes) {
            int[] out=SkyProjection.bitmapSize(input[0],input[1]);
            if(out[0]<1||out[1]<1||out[0]>1350||out[1]>1350||(long)out[0]*out[1]>850000)throw new AssertionError("bitmap bounds");
            if(input[0]>0&&input[1]>0&&input[0]<100000) {
                double ratio=(double)input[0]/input[1];
                if(Math.abs((double)out[0]/out[1]-ratio)>2.0/out[1])throw new AssertionError("aspect ratio");
            }
            cases++;
        }
        for(int az=0;az<360;az+=3)for(int alt=-90;alt<=90;alt+=3){
            boolean shown=p.horizontal(alt,az);
            if(shown&&(!Float.isFinite(p.x)||!Float.isFinite(p.y)))throw new AssertionError("non-finite");cases++;
        }
        System.out.println("PASS: "+cases+" projection/size checks; center, axes, field boundary, antipode and aspect ratio.");
    }
}
