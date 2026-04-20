// Copilot, fix project and task display:
// - Fetch projects and tasks from backend
// - Update UI immediately when a task or project is modified
// - Ensure task assignment and status changes reflect in frontend



import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Brain, 
  BookOpen, 
  Clock, 
  Target, 
  TrendingUp, 
  Plus,
  LogOut,
  User,
  MapPin,
  Calendar,
  Award,
  Activity,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { useAuth, progressApi, roadmapApi, ProgressSummary } from '@/lib/api';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [progressSummary, setProgressSummary] = useState<{
    roadmaps: ProgressSummary[];
    overall_summary: {
      total_roadmaps: number;
      total_steps: number;
      completed_steps: number;
      overall_completion_percentage: number;
    };
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProgressSummary();
    
    // Auto-refresh every 30 seconds to keep data current
    const interval = setInterval(loadProgressSummary, 30000);
    
    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  // Also refresh when the window gains focus (user returns from other tab/app)
  useEffect(() => {
    const handleFocus = () => {
      if (!loading) {
        loadProgressSummary();
      }
    };
    
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [loading]);

  const loadProgressSummary = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      
      const data = await progressApi.getUserProgressSummary();
      setProgressSummary(data);
      setError(''); // Clear any previous errors
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load progress summary';
      setError(errorMessage);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadProgressSummary(true);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getBrainTypeColor = (brainType: string) => {
    const colors = {
      Visual: 'bg-blue-100 text-blue-800',
      Auditory: 'bg-green-100 text-green-800',
      ReadWrite: 'bg-purple-100 text-purple-800',
      Kinesthetic: 'bg-orange-100 text-orange-800',
    };
    return colors[brainType as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getBrainTypeDescription = (brainType: string) => {
    const descriptions = {
      Visual: 'You learn best through visual aids, diagrams, and videos',
      Auditory: 'You learn best through listening, discussions, and audio content',
      ReadWrite: 'You learn best through reading, writing, and text-based materials',
      Kinesthetic: 'You learn best through hands-on practice and physical activities',
    };
    return descriptions[brainType as keyof typeof descriptions] || 'Your unique learning style';
  };

  const getStreakDays = () => {
    // Calculate streak based on recent activity
    if (!progressSummary?.roadmaps.length) return 0;
    
    const recentActivity = progressSummary.roadmaps.some(roadmap => {
      const lastActivity = new Date(roadmap.last_activity);
      const daysSinceActivity = Math.floor((Date.now() - lastActivity.getTime()) / (1000 * 60 * 60 * 24));
      return daysSinceActivity <= 1;
    });
    
    return recentActivity ? 5 : 0; // Simplified streak calculation
  };

  const getWeeklyProgress = () => {
    if (!progressSummary?.overall_summary) return 0;
    return Math.min(progressSummary.overall_summary.overall_completion_percentage, 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Brain className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">NeuroNav</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link 
  to="/profile"
  onClick={() => console.log("Clicked profile")}
  className="flex items-center space-x-2 cursor-pointer"
>
  <User className="h-4 w-4 text-gray-500" />
  <span className="text-sm text-gray-700">{user?.name || "Profile"}</span>
</Link>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleRefresh} 
                disabled={refreshing}
                className="text-blue-600 border-blue-200 hover:bg-blue-50"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name}! 👋
          </h2>
          <p className="text-gray-600">
            Continue your personalized learning journey
          </p>
        </div>

        {/* Brain Type Card */}
        {user?.brain_type ? (
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <Brain className="mr-2 h-5 w-5" />
                    Your Brain Type
                  </CardTitle>
                  <CardDescription>
                    Based on your assessment results
                  </CardDescription>
                </div>
                <Badge className={getBrainTypeColor(user.brain_type)}>
                  {user.brain_type} Learner
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 mb-4">
                {getBrainTypeDescription(user.brain_type)}
              </p>
              <div className="flex gap-4">
                <Button variant="outline" size="sm" asChild>
                  <Link to="/learning-tips">
                    <BookOpen className="mr-2 h-4 w-4" />
                    View Learning Tips
                  </Link>
                </Button>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/quiz">
                    <Target className="mr-2 h-4 w-4" />
                    Retake Assessment
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="mb-8 border-dashed border-2 border-blue-200">
            <CardContent className="text-center py-8">
              <Brain className="h-12 w-12 text-blue-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Discover Your Learning Style</h3>
              <p className="text-gray-600 mb-4">
                Take our brain type assessment to get personalized learning recommendations
              </p>
              <Button asChild>
                <Link to="/quiz">
                  <Plus className="mr-2 h-4 w-4" />
                  Take Assessment
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Learning Progress</p>
                  <p className="text-2xl font-bold">
                    {progressSummary?.overall_summary.completed_steps || 0}/
                    {progressSummary?.overall_summary.total_steps || 0}
                  </p>
                </div>
                <div className="p-3 bg-blue-100 rounded-full">
                  <BookOpen className="h-6 w-6 text-blue-600" />
                </div>
              </div>
              <Progress 
                value={progressSummary?.overall_summary.overall_completion_percentage || 0} 
                className="mt-4" 
              />
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Overall Progress</p>
                  <p className="text-2xl font-bold">
                    {Math.round(progressSummary?.overall_summary.overall_completion_percentage || 0)}%
                  </p>
                </div>
                <div className="p-3 bg-green-100 rounded-full">
                  <Target className="h-6 w-6 text-green-600" />
                </div>
              </div>
              <Progress value={getWeeklyProgress()} className="mt-4" />
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Learning Streak</p>
                  <p className="text-2xl font-bold">{getStreakDays()} days</p>
                </div>
                <div className="p-3 bg-orange-100 rounded-full">
                  <Award className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Roadmaps</p>
                  <p className="text-2xl font-bold">
                    {progressSummary?.overall_summary.total_roadmaps || 0}
                  </p>
                </div>
                <div className="p-3 bg-purple-100 rounded-full">
                  <MapPin className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Current Roadmaps */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MapPin className="mr-2 h-5 w-5" />
                Your Learning Roadmaps
              </CardTitle>
              <CardDescription>
                Active learning paths tailored to your brain type
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p>Loading roadmaps...</p>
                </div>
              ) : progressSummary?.roadmaps.length ? (
                <div className="space-y-4">
                  {progressSummary.roadmaps.map((roadmap) => (
                    <div key={roadmap.roadmap_id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{roadmap.roadmap_title}</h4>
                        <Badge 
                          variant={roadmap.completion_percentage === 100 ? "default" : "secondary"}
                          className={roadmap.completion_percentage === 100 ? "bg-green-100 text-green-800" : ""}
                        >
                          {roadmap.completion_percentage === 100 ? (
                            <>
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                              Complete
                            </>
                          ) : (
                            'In Progress'
                          )}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        Personalized for {roadmap.brain_type} learners
                      </p>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center text-sm text-gray-500">
                          <Activity className="h-4 w-4 mr-1" />
                          {roadmap.completed_steps}/{roadmap.total_steps} steps completed
                        </div>
                        <Button size="sm" variant="outline" asChild>
                          <Link to={`/roadmap/${roadmap.roadmap_id}`}>
                            {roadmap.completion_percentage === 100 ? 'Review' : 'Continue'}
                          </Link>
                        </Button>
                      </div>
                      <Progress value={roadmap.completion_percentage} className="h-2" />
                      <p className="text-xs text-gray-500 mt-2">
                        {Math.round(roadmap.completion_percentage)}% complete
                      </p>
                    </div>
                  ))}
                  
                  <Button variant="outline" className="w-full" asChild>
                    <Link to="/quiz">
                      <Plus className="mr-2 h-4 w-4" />
                      Create New Roadmap
                    </Link>
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8">
                  <MapPin className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">No roadmaps yet</p>
                  <Button asChild>
                    <Link to="/quiz">Take Assessment First</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="mr-2 h-5 w-5" />
                Recent Activity
              </CardTitle>
              <CardDescription>
                Your latest learning milestones
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {progressSummary?.roadmaps.length ? (
                  progressSummary.roadmaps.slice(0, 3).map((roadmap, index) => (
                    <div key={roadmap.roadmap_id} className="flex items-start space-x-3">
                      <div className={`p-2 rounded-full ${
                        roadmap.completion_percentage === 100 
                          ? 'bg-green-100' 
                          : roadmap.completion_percentage > 50 
                            ? 'bg-blue-100' 
                            : 'bg-gray-100'
                      }`}>
                        {roadmap.completion_percentage === 100 ? (
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                        ) : roadmap.completion_percentage > 50 ? (
                          <BookOpen className="h-4 w-4 text-blue-600" />
                        ) : (
                          <Target className="h-4 w-4 text-gray-600" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">
                          {roadmap.completion_percentage === 100 
                            ? `Completed: ${roadmap.roadmap_title}`
                            : `Progress in: ${roadmap.roadmap_title}`
                          }
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(roadmap.last_activity).toLocaleDateString()} • {roadmap.completion_percentage}% complete
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <>
                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-blue-100 rounded-full">
                        <Brain className="h-4 w-4 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">Welcome to NeuroNav!</p>
                        <p className="text-xs text-gray-500">Take your first assessment to get started</p>
                      </div>
                    </div>
                  </>
                )}
                
                {!user?.brain_type && (
                  <div className="border-t pt-4">
                    <div className="text-center">
                      <Calendar className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">
                        Take the assessment to start tracking your progress
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}