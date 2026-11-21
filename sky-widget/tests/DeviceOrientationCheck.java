package de.universelab.sternfenster;

import java.util.Arrays;
import java.util.Random;

/** Run with javac/java alone; no Android runtime, sensor emulator or test framework. */
public final class DeviceOrientationCheck {
    private static int checks;
    private static final double[] EAST = {1, 0, 0}, NORTH = {0, 1, 0}, UP = {0, 0, 1};

    private static void close(double got, double expected, String name) {
        checks++;
        if (!Double.isFinite(got) || Math.abs(got - expected) > 2e-6)
            throw new AssertionError(name + ": " + got + " vs " + expected);
    }
    private static void truth(boolean condition, String name) {
        checks++;
        if (!condition) throw new AssertionError(name);
    }
    private static void vector(double[] actual, int offset, double[] expected, String name) {
        for (int i = 0; i < 3; i++) close(actual[offset + i], expected[i], name + "[" + i + "]");
    }
    private static void pixel(double got,double expected,String name) {
        checks++;
        if (!Double.isFinite(got) || Math.abs(got-expected)>.003)
            throw new AssertionError(name+": "+got+" vs "+expected);
    }
    private static void projectionChecks(double[] basis) {
        int width=720,height=1000;
        double fov=100;
        SkyProjection projection=new SkyProjection(width,height,fov,basis);
        truth(projection.project(basis[0],basis[1],basis[2]),"camera center rejected");
        pixel(projection.x,width*.5,"camera center x");
        pixel(projection.y,height*.5,"camera center y");
        // Camera rays through all four rectangular field edges and corners.
        // These must retain the same pixel locations at every pointing and roll.
        for (int[] edge:new int[][]{{1,0},{-1,0},{0,1},{0,-1},{1,1},{1,-1},{-1,1},{-1,-1}}) {
            double right=edge[0]*width*.5,top=edge[1]*height*.5;
            double distance=Math.hypot(right,top),angle=Math.toRadians(fov)*distance/height;
            double c=Math.cos(angle),s=Math.sin(angle)/distance;
            double e=c*basis[0]+s*(right*basis[3]+top*basis[6]);
            double n=c*basis[1]+s*(right*basis[4]+top*basis[7]);
            double u=c*basis[2]+s*(right*basis[5]+top*basis[8]);
            truth(projection.project(e,n,u),"valid field-edge ray rejected");
            pixel(projection.x,width*.5+right,"field edge x");
            pixel(projection.y,height*.5-top,"field edge y");
        }
        truth(!projection.project(-basis[0],-basis[1],-basis[2]),"camera antipode accepted");
    }
    private static double[] minus(double[] v) { return new double[]{-v[0], -v[1], -v[2]}; }
    private static double dot(double[] a, int x, double[] b, int y) {
        return a[x] * b[y] + a[x + 1] * b[y + 1] + a[x + 2] * b[y + 2];
    }
    private static float[] columns(double[] x, double[] y, double[] z) {
        return new float[]{(float)x[0], (float)y[0], (float)z[0],
                (float)x[1], (float)y[1], (float)z[1],
                (float)x[2], (float)y[2], (float)z[2]};
    }
    private static float[] as16(float[] m) {
        return new float[]{m[0],m[1],m[2],0, m[3],m[4],m[5],0, m[6],m[7],m[8],0, 0,0,0,1};
    }
    private static double[] pose(float[] matrix, int rotation, double declination) {
        double[] out = new double[9];
        truth(DeviceOrientationMath.cameraBasis(matrix, rotation, declination, out), "valid matrix rejected");
        for (int i = 0; i < 9; i += 3) close(dot(out,i,out,i),1,"unit basis");
        close(dot(out,0,out,3),0,"forward/right perpendicular");
        close(dot(out,0,out,6),0,"forward/up perpendicular");
        close(dot(out,3,out,6),0,"right/up perpendicular");
        // Camera basis right x up points back towards the viewer, hence -forward.
        close(out[4]*out[8]-out[5]*out[7],-out[0],"handedness east");
        close(out[5]*out[6]-out[3]*out[8],-out[1],"handedness north");
        close(out[3]*out[7]-out[4]*out[6],-out[2],"handedness up");
        return out;
    }
    private static void heading(float[] matrix, double expectedAz, double expectedAlt) {
        double[] out = pose(matrix,0,0);
        close(DeviceOrientationMath.azimuth(out,123),expectedAz,"heading");
        close(DeviceOrientationMath.altitude(out),expectedAlt,"altitude");
    }
    // Independent physical reference: Rodrigues rotation of an ENU vector about
    // a unit world axis. The helper instead reads Android matrix columns.
    private static double[] rotate(double[] v, double[] axis, double radians) {
        double c = Math.cos(radians), s = Math.sin(radians), k = (1-c)*dot(axis,0,v,0);
        return new double[]{v[0]*c + (axis[1]*v[2]-axis[2]*v[1])*s + axis[0]*k,
                v[1]*c + (axis[2]*v[0]-axis[0]*v[2])*s + axis[1]*k,
                v[2]*c + (axis[0]*v[1]-axis[1]*v[0])*s + axis[2]*k};
    }
    private static double[] quaternionRotate(double[] v, double[] q) {
        // Independent quaternion/vector action: v + 2w(qv x v) + 2qv x(qv x v).
        double x=q[2]*v[2]-q[3]*v[1], y=q[3]*v[0]-q[1]*v[2], z=q[1]*v[1]-q[2]*v[0];
        return new double[]{v[0]+2*q[0]*x+2*(q[2]*z-q[3]*y),
                v[1]+2*q[0]*y+2*(q[3]*x-q[1]*z),
                v[2]+2*q[0]*z+2*(q[1]*y-q[2]*x)};
    }
    private static double[] axisQuaternion(double[] axis,double degrees) {
        double half=Math.toRadians(degrees)*.5,s=Math.sin(half);
        return new double[]{Math.cos(half),axis[0]*s,axis[1]*s,axis[2]*s};
    }
    private static void quaternionEquivalent(double[] a,double[] b,String name) {
        for (double[] v : new double[][]{EAST,NORTH,UP})
            vector(quaternionRotate(v,a),0,quaternionRotate(v,b),name);
    }
    private static void quaternionChecks() {
        double[] q=new double[4],identity={1,0,0,0},output=new double[4];
        for (double[] axis:new double[][]{EAST,NORTH,UP}) {
            for (double degrees:new double[]{0,90,-90,180,-180,179.999,181,359}) {
                double angle=Math.toRadians(degrees);
                float[] matrix=columns(rotate(EAST,axis,angle),rotate(NORTH,axis,angle),rotate(UP,axis,angle));
                for (float[] input:new float[][]{matrix,as16(matrix)}) {
                    truth(DeviceOrientationMath.quaternionFromMatrix(input,q),"known matrix quaternion");
                    quaternionEquivalent(q,axisQuaternion(axis,degrees),"known physical quaternion");
                    for (double[] v:new double[][]{EAST,NORTH,UP})
                        vector(quaternionRotate(v,q),0,rotate(v,axis,angle),"matrix/quaternion roundtrip");
                }
            }
        }
        double[] ninety=axisQuaternion(EAST,90),negative=ninety.clone();
        for (int i=0;i<4;i++)negative[i]=-negative[i];
        truth(DeviceOrientationMath.blendQuaternion(identity,ninety,.5,output),"blend ninety");
        quaternionEquivalent(output,axisQuaternion(EAST,45),"halfway ninety is forty-five");
        truth(DeviceOrientationMath.blendQuaternion(identity,negative,.5,output),"negative sign blend");
        quaternionEquivalent(output,axisQuaternion(EAST,45),"q and minus q same blend");
        truth(DeviceOrientationMath.blendQuaternion(ninety,negative,.5,output),"opposite sign no zero");
        quaternionEquivalent(output,ninety,"opposite sign same pose");
        truth(DeviceOrientationMath.blendQuaternion(identity,axisQuaternion(UP,180),.5,output),"halfway180");
        quaternionEquivalent(output,axisQuaternion(UP,90),"halfway180 is ninety");
        truth(DeviceOrientationMath.blendQuaternion(axisQuaternion(UP,170),axisQuaternion(UP,-170),.5,output),"across180");
        quaternionEquivalent(output,axisQuaternion(UP,180),"shortest path across180");
        double[] alias=identity.clone();
        truth(DeviceOrientationMath.blendQuaternion(alias,ninety,.5,alias),"out aliases from");
        quaternionEquivalent(alias,axisQuaternion(EAST,45),"from alias result");
        alias=ninety.clone();
        truth(DeviceOrientationMath.blendQuaternion(identity,alias,.5,alias),"out aliases target");
        quaternionEquivalent(alias,axisQuaternion(EAST,45),"target alias result");
        truth(DeviceOrientationMath.blendQuaternion(identity,ninety,-2,output),"negative alpha");
        quaternionEquivalent(output,identity,"clamp alpha below0");
        truth(DeviceOrientationMath.blendQuaternion(identity,ninety,2,output),"large alpha");
        quaternionEquivalent(output,ninety,"clamp alpha above1");
        double[] scaled=ninety.clone();
        for(int i=0;i<4;i++)scaled[i]*=7;
        truth(DeviceOrientationMath.blendQuaternion(new double[]{2,0,0,0},scaled,.5,output),"normalize both inputs");
        quaternionEquivalent(output,axisQuaternion(EAST,45),"scaled blend result");
        double[] sentinel={4,3,2,1};
        for (double[] bad:new double[][]{null,new double[3],new double[4],{Double.NaN,0,0,0},{1,Double.POSITIVE_INFINITY,0,0}}) {
            double[] result=sentinel.clone();
            truth(!DeviceOrientationMath.blendQuaternion(bad,ninety,.5,result),"invalid from accepted");
            truth(Arrays.equals(result,sentinel),"invalid from modified output");
            truth(!DeviceOrientationMath.blendQuaternion(identity,bad,.5,result),"invalid target accepted");
            truth(Arrays.equals(result,sentinel),"invalid target modified output");
        }
        double[] result=sentinel.clone();
        truth(!DeviceOrientationMath.blendQuaternion(identity,ninety,Double.NaN,result),"NaN alpha accepted");
        truth(Arrays.equals(result,sentinel),"NaN alpha modified output");
        truth(!DeviceOrientationMath.blendQuaternion(identity,ninety,.5,null),"null blend output accepted");
        truth(!DeviceOrientationMath.quaternionFromMatrix(null,result),"null matrix accepted");
        truth(!DeviceOrientationMath.quaternionFromMatrix(new float[9],result),"zero matrix accepted");
        truth(Arrays.equals(result,sentinel),"invalid matrix modified quaternion");
        truth(!DeviceOrientationMath.quaternionFromMatrix(new float[]{1,0,0,0,1,0,0,0,-1},result),"reflection quaternion accepted");
        truth(Arrays.equals(result,sentinel),"reflection modified quaternion");
    }
    private static void invalid(float[] matrix, int rotation, double declination) {
        double[] out = {9,8,7,6,5,4,3,2,1}, before = out.clone();
        truth(!DeviceOrientationMath.cameraBasis(matrix,rotation,declination,out),"invalid input accepted");
        truth(Arrays.equals(out,before),"failure modified last good pose");
    }

    public static void main(String[] args) {
        quaternionChecks();
        float[] north = {1,0,0, 0,0,-1, 0,1,0};
        heading(north,0,0);
        heading(new float[]{0,0,-1, -1,0,0, 0,1,0},90,0);
        heading(new float[]{-1,0,0, 0,0,1, 0,1,0},180,0);
        heading(new float[]{0,0,1, 1,0,0, 0,1,0},270,0);

        // Known physical north-facing rotations: up 45 degrees, down 30 degrees.
        double s = Math.sqrt(.5);
        heading(columns(EAST,new double[]{0,-s,s},new double[]{0,-s,-s}),0,45);
        heading(columns(EAST,new double[]{0,.5,Math.sqrt(.75)},
                new double[]{0,-Math.sqrt(.75),.5}),0,-30);

        // Camera points behind the display, not along the phone's upper edge.
        double[] nadir = pose(new float[]{1,0,0, 0,1,0, 0,0,1},0,0);
        vector(nadir,0,new double[]{0,0,-1},"face-up phone looks down");
        close(DeviceOrientationMath.altitude(nadir),-90,"nadir altitude");
        close(DeviceOrientationMath.azimuth(nadir,287),287,"nadir retains heading");
        double[] zenith = pose(new float[]{1,0,0, 0,-1,0, 0,0,-1},0,0);
        vector(zenith,0,UP,"face-down phone looks up");
        close(DeviceOrientationMath.altitude(zenith),90,"zenith altitude");
        close(DeviceOrientationMath.azimuth(zenith,287),287,"zenith retains heading");
        projectionChecks(zenith); projectionChecks(nadir);

        // Physical left rotation gives Surface.ROTATION_90 (graphics turn right).
        // The same visible north-facing screen basis must survive all four modes.
        float[][] physicallyTurned = {north,
                {0,-1,0, 0,0,-1, 1,0,0},
                {-1,0,0, 0,0,-1, 0,-1,0},
                {0,1,0, 0,0,-1, -1,0,0}};
        for (int rotation = 0; rotation < 4; rotation++) {
            double[] out = pose(physicallyTurned[rotation],rotation,0);
            vector(out,0,NORTH,"display-independent forward");
            vector(out,3,EAST,"display-compensated right");
            vector(out,6,UP,"display-compensated up");
            projectionChecks(out);
        }

        // With rotation locked, a clockwise handset roll stays in the basis.
        double[] rolled = pose(physicallyTurned[3],0,0);
        vector(rolled,0,NORTH,"roll preserves pointing");
        vector(rolled,3,minus(UP),"clockwise rolled screen right");
        vector(rolled,6,EAST,"clockwise rolled screen top");
        projectionChecks(rolled);

        double[] corrected = pose(north,0,12);
        close(DeviceOrientationMath.azimuth(corrected,0),12,"east-positive declination");
        corrected = pose(north,0,-12);
        close(DeviceOrientationMath.azimuth(corrected,0),348,"west-negative declination");
        corrected = pose(north,0,372);
        close(DeviceOrientationMath.azimuth(corrected,0),12,"declination wraps");
        close(DeviceOrientationMath.shortestDeltaDegrees(359,1),2,"north seam forward");
        close(DeviceOrientationMath.shortestDeltaDegrees(1,359),-2,"north seam backward");

        // Dense independent orientation / roll / display / declination checks.
        Random random = new Random(731_031);
        for (int sample = 0; sample < 1500; sample++) {
            double[] axis = {random.nextDouble()*2-1,random.nextDouble()*2-1,random.nextDouble()*2-1};
            double norm = Math.sqrt(dot(axis,0,axis,0));
            for (int i = 0; i < 3; i++) axis[i] /= norm;
            double angle = (random.nextDouble()*2-1)*Math.PI;
            double declination = random.nextDouble()*50-25;
            double[] physicalRight = rotate(EAST,axis,angle);
            double[] physicalUp = rotate(UP,axis,angle);
            double[] physicalForward = rotate(NORTH,axis,angle);
            float[] matrix = columns(physicalRight,physicalUp,minus(physicalForward));
            double[] quaternion=new double[4];
            truth(DeviceOrientationMath.quaternionFromMatrix(matrix,quaternion),"random matrix quaternion");
            vector(quaternionRotate(EAST,quaternion),0,physicalRight,"random quaternion right");
            vector(quaternionRotate(NORTH,quaternion),0,physicalUp,"random quaternion device top");
            vector(quaternionRotate(UP,quaternion),0,minus(physicalForward),"random quaternion device front");
            double[] testVector={.17,-.37,.91};
            double[] inverse={quaternion[0],-quaternion[1],-quaternion[2],-quaternion[3]};
            vector(quaternionRotate(quaternionRotate(testVector,quaternion),inverse),0,testVector,"quaternion inverse");
            int display = sample%4;
            double[] out = pose(sample%2==0?matrix:as16(matrix),display,declination);
            projectionChecks(out);
            double[] expectedRight = display==0?physicalRight:display==1?minus(physicalUp):
                    display==2?minus(physicalRight):physicalUp;
            double[] expectedUp = display==0?physicalUp:display==1?physicalRight:
                    display==2?minus(physicalUp):minus(physicalRight);
            vector(out,0,rotate(physicalForward,UP,-Math.toRadians(declination)),"independent forward");
            vector(out,3,rotate(expectedRight,UP,-Math.toRadians(declination)),"independent screen right");
            vector(out,6,rotate(expectedUp,UP,-Math.toRadians(declination)),"independent screen up");
            // The selected orientation must reconstruct a world direction after
            // camera-space conversion; a row/column or sign error fails this.
            double[] world = {.31,-.22,.83};
            double f = dot(world,0,out,0), r = dot(world,0,out,3), u = dot(world,0,out,6);
            for (int i = 0; i < 3; i++)
                close(f*out[i]+r*out[3+i]+u*out[6+i],world[i],"world/camera roundtrip");
        }

        // Crossing the zenith remains a continuous basis even as azimuth flips.
        double[] previous = null;
        for (int hundredth = 8990; hundredth <= 9010; hundredth++) {
            double angle = Math.toRadians(hundredth/100.0);
            double[] forward = {0,Math.cos(angle),Math.sin(angle)};
            double[] top = {0,-Math.sin(angle),Math.cos(angle)};
            double[] out = pose(columns(EAST,top,minus(forward)),0,0);
            vector(out,0,forward,"zenith passage forward");
            vector(out,6,top,"zenith passage top");
            if (previous != null) {
                double squared = 0;
                for (int i = 0; i < 9; i++) squared += (out[i]-previous[i])*(out[i]-previous[i]);
                truth(squared < 1e-6,"basis jumped at zenith");
            }
            previous = out;
        }

        invalid(null,0,0); invalid(new float[8],0,0); invalid(new float[9],0,0);
        invalid(north,-1,0); invalid(north,4,0); invalid(north,0,Double.NaN);
        float[] reflected = north.clone(); reflected[0]=-1; invalid(reflected,0,0);
        float[] nonfinite = north.clone(); nonfinite[4]=Float.NaN; invalid(nonfinite,0,0);
        float[] sheared = north.clone(); sheared[1]=.2f; invalid(sheared,0,0);
        float[] scaled = north.clone(); scaled[0]=2; invalid(scaled,0,0);
        truth(!DeviceOrientationMath.cameraBasis(north,0,0,null),"null output accepted");
        truth(!DeviceOrientationMath.cameraBasis(north,0,0,new double[8]),"short output accepted");
        System.out.println("PASS: " + checks + " device orientation/projection checks; cardinal/tilt/roll, display rotations, declination, poles, 9/16 matrices, quaternion sign/180-degree/alias/inverse/roundtrip, camera field edges/corners, invalid input, and 1500 physical Rodrigues poses.");
    }
}
