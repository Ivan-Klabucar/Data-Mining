package se.kth.jabeja;

import org.apache.log4j.Logger;
import se.kth.jabeja.config.Config;
import se.kth.jabeja.config.NodeSelectionPolicy;
import se.kth.jabeja.io.FileIO;
import se.kth.jabeja.rand.RandNoGenerator;

import java.io.File;
import java.io.IOException;
import java.util.*;
import java.lang.Math;

public class Jabeja {
  final static Logger logger = Logger.getLogger(Jabeja.class);
  private final Config config;
  private final HashMap<Integer/*id*/, Node/*neighbors*/> entireGraph;
  private final List<Integer> nodeIds;
  private int numberOfSwaps;
  private int round;
  private float T;
  private float T_min;
  private double C;
  private Integer bestEdgeCut;
  private Integer lastNumberOfSwaps;
  private int no_change_counter = 0;
  private boolean resultFileCreated = false;

  //-------------------------------------------------------------------
  public Jabeja(HashMap<Integer, Node> graph, Config config) {
    this.entireGraph = graph;
    this.nodeIds = new ArrayList(entireGraph.keySet());
    this.round = 0;
    this.numberOfSwaps = 0;
    this.config = config;
    this.reset_annealing();
  }


  //-------------------------------------------------------------------
  public void startJabeja() throws IOException {
    for (round = 0; round < config.getRounds(); round++) {
      for (int id : entireGraph.keySet()) {
        sampleAndSwap(id);
      }

      //one cycle for all nodes have completed.
      //reduce the temperature
      saCoolDown();
      report();
    }
  }

  public void reset_annealing() {
    this.T = config.getTemperature();
    if (config.getDiffAnnealing()) {
      this.T = 1;
      this.T_min = (float) 0.00001;
    }
    if(config.getCustomAccFunc() != null) {
      this.C = config.getCustomAccFunc();
    }
  }

  public double getAcceptance(double new_score, double old_score) {
    if (config.getCustomAccFunc() != null) return Math.exp(this.C + (new_score - old_score) / T);
    return Math.exp((new_score - old_score) / T);
  }

  /**
   * Simulated analealing cooling function
   */
  private void saCoolDown(){
    // TODO for second task
    if (config.getDiffAnnealing()) { // Use different annealing mechanism described in task 2
      T *= config.getDelta();
      if (T < T_min) {
        T = T_min;
      }

      if(config.getCustomAccFunc() != null) {
        this.C -= config.getCustomAccFunc() / 100;
        if (this.C < 0) {
          this.C = 0;
        }
      }

    } else {
      if (T > 1)
        T -= config.getDelta();
      if (T < 1)
        T = 1;
    }
  }

  /**
   * Sample and swap algorith at node p
   * @param nodeId
   */
  private void sampleAndSwap(int nodeId) {
    Node partner = null;
    Node nodep = entireGraph.get(nodeId);

    if (config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
            || config.getNodeSelectionPolicy() == NodeSelectionPolicy.LOCAL) {
      partner = this.findPartner(nodeId, this.getNeighbors(nodep));
    }

    if (config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
            || config.getNodeSelectionPolicy() == NodeSelectionPolicy.RANDOM) {
      if (partner == null) {
        partner = this.findPartner(nodeId, this.getSample(nodeId));
      }
    }

    if (partner != null){
      int partner_color = partner.getColor();
      int curr_color = nodep.getColor();
      nodep.setColor(partner_color);
      partner.setColor(curr_color);
      this.numberOfSwaps += 1;
    }
  }

  public Node findPartner(int nodeId, Integer[] nodes){

    double a = config.getAlpha();

    Node nodep = entireGraph.get(nodeId);
    int d_pp = this.getDegree(nodep, nodep.getColor());
    

    Node bestPartner = null;
    double highestBenefit = 0;

    for (int q : nodes){
      Node nodeq = entireGraph.get(q);
      int d_qq = this.getDegree(nodeq, nodeq.getColor());
      double old_score = Math.pow(d_pp, a) + Math.pow(d_qq, a);
      int d_pq = this.getDegree(nodep, nodeq.getColor());
      int d_qp = this.getDegree(nodeq, nodep.getColor());
      double new_score = Math.pow(d_pq, a) + Math.pow(d_qp, a);
      if (config.getDiffAnnealing()) {
        double acceptance = this.getAcceptance(new_score, old_score);
        if (new_score != old_score && acceptance > Math.random() && acceptance > highestBenefit) {
          bestPartner = nodeq;
          highestBenefit = acceptance;
        }
      } else {
        if ((new_score * T) > old_score && new_score > highestBenefit) {
          bestPartner = nodeq;
          highestBenefit = new_score;
        }
      }
    }

    return bestPartner;
  }

  /**
   * The the degreee on the node based on color
   * @param node
   * @param colorId
   * @return how many neighbors of the node have color == colorId
   */
  private int getDegree(Node node, int colorId){
    int degree = 0;
    for(int neighborId : node.getNeighbours()){
      Node neighbor = entireGraph.get(neighborId);
      if(neighbor.getColor() == colorId){
        degree++;
      }
    }
    return degree;
  }

  /**
   * Returns a uniformly random sample of the graph
   * @param currentNodeId
   * @return Returns a uniformly random sample of the graph
   */
  private Integer[] getSample(int currentNodeId) {
    int count = config.getUniformRandomSampleSize();
    int rndId;
    int size = entireGraph.size();
    ArrayList<Integer> rndIds = new ArrayList<Integer>();

    while (true) {
      rndId = nodeIds.get(RandNoGenerator.nextInt(size));
      if (rndId != currentNodeId && !rndIds.contains(rndId)) {
        rndIds.add(rndId);
        count--;
      }

      if (count == 0)
        break;
    }

    Integer[] ids = new Integer[rndIds.size()];
    return rndIds.toArray(ids);
  }

  /**
   * Get random neighbors. The number of random neighbors is controlled using
   * -closeByNeighbors command line argument which can be obtained from the config
   * using {@link Config#getRandomNeighborSampleSize()}
   * @param node
   * @return
   */
  private Integer[] getNeighbors(Node node) {
    ArrayList<Integer> list = node.getNeighbours();
    int count = config.getRandomNeighborSampleSize();
    int rndId;
    int index;
    int size = list.size();
    ArrayList<Integer> rndIds = new ArrayList<Integer>();

    if (size <= count)
      rndIds.addAll(list);
    else {
      while (true) {
        index = RandNoGenerator.nextInt(size);
        rndId = list.get(index);
        if (!rndIds.contains(rndId)) {
          rndIds.add(rndId);
          count--;
        }

        if (count == 0)
          break;
      }
    }

    Integer[] arr = new Integer[rndIds.size()];
    return rndIds.toArray(arr);
  }


  /**
   * Generate a report which is stored in a file in the output dir.
   *
   * @throws IOException
   */
  private void report() throws IOException {
    int grayLinks = 0;
    int migrations = 0; // number of nodes that have changed the initial color
    int size = entireGraph.size();

    for (int i : entireGraph.keySet()) {
      Node node = entireGraph.get(i);
      int nodeColor = node.getColor();
      ArrayList<Integer> nodeNeighbours = node.getNeighbours();

      if (nodeColor != node.getInitColor()) {
        migrations++;
      }

      if (nodeNeighbours != null) {
        for (int n : nodeNeighbours) {
          Node p = entireGraph.get(n);
          int pColor = p.getColor();

          if (nodeColor != pColor)
            grayLinks++;
        }
      }
    }

    int edgeCut = grayLinks / 2;
    if (bestEdgeCut == null || edgeCut < bestEdgeCut) {
      bestEdgeCut = edgeCut;
    }

    if (lastNumberOfSwaps != null) {
      if (numberOfSwaps == lastNumberOfSwaps) no_change_counter += 1;
      if (no_change_counter > 10 && config.getRstAnnealing()) {
        this.reset_annealing();
        no_change_counter = 0;
      }
    }
    lastNumberOfSwaps = numberOfSwaps;

    logger.info("round: " + round +
            ", edge cut:" + edgeCut +
            ", swaps: " + numberOfSwaps +
            ", migrations: " + migrations +
            ", best edge cut:" + bestEdgeCut +
            ", T:" + T);

    saveToFile(edgeCut, migrations);
  }

  private void saveToFile(int edgeCuts, int migrations) throws IOException {
    String delimiter = "\t\t";
    String outputFilePath;

    //output file name
    File inputFile = new File(config.getGraphFilePath());
    outputFilePath = config.getOutputDir() +
            File.separator +
            inputFile.getName() + "_" +
            "NS" + "_" + config.getNodeSelectionPolicy() + "_" +
            "GICP" + "_" + config.getGraphInitialColorPolicy() + "_" +
            "T" + "_" + config.getTemperature() + "_" +
            "D" + "_" + config.getDelta() + "_" +
            "RNSS" + "_" + config.getRandomNeighborSampleSize() + "_" +
            "URSS" + "_" + config.getUniformRandomSampleSize() + "_" +
            "A" + "_" + config.getAlpha() + "_" +
            "R" + "_" + config.getRounds() + ".txt";

    if (!resultFileCreated) {
      File outputDir = new File(config.getOutputDir());
      if (!outputDir.exists()) {
        if (!outputDir.mkdir()) {
          throw new IOException("Unable to create the output directory");
        }
      }
      // create folder and result file with header
      String header = "# Migration is number of nodes that have changed color.";
      header += "\n\nRound" + delimiter + "Edge-Cut" + delimiter + "Swaps" + delimiter + "Migrations" + delimiter + "Skipped" + "\n";
      FileIO.write(header, outputFilePath);
      resultFileCreated = true;
    }

    FileIO.append(round + delimiter + (edgeCuts) + delimiter + numberOfSwaps + delimiter + migrations + "\n", outputFilePath);
  }
}
