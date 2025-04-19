package com.sjtuctf2025.smartgrader.controller;

import java.util.ArrayList;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping({"/api"})
public class GraderController {
   @PostMapping({"/grader"})
   public ArrayList<String> grader(@RequestBody String body) {
      ArrayList results = new ArrayList();

      try {
         JSONObject json = new JSONObject(body);
         JSONArray scores = json.getJSONArray("scores");
         JSONArray rules = json.getJSONArray("rules");
         if (rules.length() > 10) {
            System.out.println("Too many rules!");
            return results;
         }

         for(int i = 0; i < scores.length(); ++i) {
            Double score = scores.getDouble(i);
            results.add(this.grade(score, rules));
         }
      } catch (Exception var8) {
         System.out.println(var8.getMessage());
      }

      return results;
   }

   private String grade(Double score, JSONArray rules) {
      try {
         for(int i = 0; i < rules.length(); ++i) {
            JSONObject rule = rules.getJSONObject(i);
            String leftSymbol = rule.getString("leftSymbol");
            String rightSymbol = rule.getString("rightSymbol");
            Double leftScore = rule.getDouble("leftScore");
            Double rightScore = rule.getDouble("rightScore");
            String grade = rule.getString("grade");
            if (this.script(score, leftSymbol, rightSymbol, leftScore, rightScore)) {
               return grade;
            }
         }
      } catch (Exception var10) {
         System.out.println(var10.getMessage());
      }

      return "N/A";
   }

   private boolean script(Double score, String leftSymbol, String rightSymbol, Double leftScore, Double rightScore) {
      if (leftSymbol.length() <= 24 && rightSymbol.length() <= 24) {
         String expr = "(" + leftScore + leftSymbol + "x && x" + rightSymbol + rightScore + ")";
         ScriptEngineManager manager = new ScriptEngineManager();
         ScriptEngine engine = manager.getEngineByName("js");
         engine.put("x", score);

         try {
            Object result = engine.eval(expr);
            return result.toString().equals("true");
         } catch (Exception var10) {
            System.out.println(var10.getMessage());
            return false;
         }
      } else {
         System.out.println("Symbol too long!");
         return false;
      }
   }
}
