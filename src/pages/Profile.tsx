import { useAuth } from "@/lib/api";

const user = {
  name: "Alex Johnson",
  email: "alex@example.com",
  role: "Senior Product Designer",
  joinedAt: "January 2023",
  bio: "Building thoughtful digital products with a focus on user-centered design and clean systems. Open to collaborations.",
  brainType: "Analytical",
  timezone: "IST (UTC +5:30)",
  location: "Pune, India",
  dob: "March 14, 1995",
  language: "English, Hindi",
  skills: ["Figma", "React", "TypeScript", "User Research", "Design Systems", "Prototyping", "Tailwind CSS"],
  stats: { projects: 142, followers: "3.4k", completion: "98%" },
  profileCompletion: 80,
  socials: [
    { label: "GitHub", href: "#" },
    { label: "LinkedIn", href: "#" },
    { label: "Twitter / X", href: "#" },
  ],
};

const fields = [
  { label: "Full name", value: user.name },
  { label: "Email", value: user.email },
  { label: "Brain type", value: user.brainType },
  { label: "Timezone", value: user.timezone },
  { label: "Location", value: user.location },
  { label: "Date of birth", value: user.dob },
  { label: "Language", value: user.language },
];

function Avatar({ name }: { name: string }) {
  return (
    <div className="w-16 h-16 rounded-full bg-blue-700 text-blue-100 flex items-center justify-center text-2xl font-medium flex-shrink-0">
      {name.charAt(0)}
    </div>
  );
}

function StatCard({ num, label }: { num: string | number; label: string }) {
  return (
    <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-3 text-center">
      <p className="text-xl font-medium text-gray-900 dark:text-gray-100">{num}</p>
      <p className="text-xs text-gray-500 mt-0.5">{label}</p>
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[11px] font-medium text-gray-400 uppercase tracking-widest mb-3">
      {children}
    </p>
  );
}

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl p-5">
      {children}
    </div>
  );
}

export default function Profile() {
  const completion = user.profileCompletion;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950 py-6 px-4">
      <div className="max-w-2xl mx-auto flex flex-col gap-4">

        {/* Header */}
        <Card>
          <div className="flex items-center gap-4 mb-4">
            <Avatar name={user.name} />
            <div className="flex-1">
              <div className="flex items-center flex-wrap gap-2">
                <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                  {user.name}
                </h2>
                <span className="text-xs px-2.5 py-0.5 rounded-md bg-green-50 text-green-700 font-medium">
                  Active
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-md bg-blue-50 text-blue-700 font-medium">
                  Pro
                </span>
              </div>
              <p className="text-sm text-gray-500 mt-0.5">{user.role}</p>
              <p className="text-xs text-gray-400 mt-0.5">Joined {user.joinedAt}</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 leading-relaxed mb-4">{user.bio}</p>
          <div className="flex flex-wrap gap-2">
            <button className="px-4 py-2 rounded-lg bg-blue-700 text-blue-50 text-sm font-medium hover:bg-blue-800 transition">
              Edit profile
            </button>
            <button className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition">
              Change password
            </button>
            <button className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition">
              Share profile
            </button>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-2.5">
          <StatCard num={user.stats.projects} label="Projects" />
          <StatCard num={user.stats.followers} label="Followers" />
          <StatCard num={user.stats.completion} label="Completion" />
        </div>

        {/* Personal Info */}
        <Card>
          <SectionLabel>Personal information</SectionLabel>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {fields.map(({ label, value }) => (
              <div key={label} className="flex justify-between items-center py-2.5 first:pt-0 last:pb-0">
                <span className="text-sm text-gray-500">{label}</span>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{value}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Profile Completion */}
        <Card>
          <SectionLabel>Profile completion</SectionLabel>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-sm text-gray-500">Your profile is {completion}% complete</span>
            <span className="text-sm font-medium text-blue-700">{completion}%</span>
          </div>
          <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full transition-all duration-500"
              style={{ width: `${completion}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Add a phone number and portfolio link to complete your profile.
          </p>
        </Card>

        {/* Skills */}
        <Card>
          <SectionLabel>Skills</SectionLabel>
          <div className="flex flex-wrap gap-2">
            {user.skills.map((skill) => (
              <span
                key={skill}
                className="px-3 py-1 text-xs text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800"
              >
                {skill}
              </span>
            ))}
          </div>
        </Card>

        {/* Linked Accounts */}
        {/* <Card>
          <SectionLabel>Linked accounts</SectionLabel>
          <div className="flex flex-wrap gap-2">
            {user.socials.map(({ label, href }) => (
              
                key={label}
                href={href}
                className="flex items-center gap-2 px-3 py-1.5 text-xs text-gray-500 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              >
                {label}
              </a>
            ))}
          </div>
        </Card> */}

      </div>
    </div>
  );
}